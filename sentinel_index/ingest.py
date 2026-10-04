"""
Incremental ingestion pipeline (PS 2.2.6).
Takes new GeoTIFFs, extracts tiles, calculates stats, embeds, and appends to FAISS + SQLite.
"""
import time
from pathlib import Path

import faiss
import numpy as np
import rasterio
from PIL import Image

from . import config, db, embed, quality


def load_index():
    if config.FAISS_PATH.exists():
        return faiss.read_index(str(config.FAISS_PATH))
    # Inner Product (IP) index for cosine similarity, since embeddings are L2-normalized
    return faiss.IndexFlatIP(config.EMBED_DIM)


def ingest_scene(scene_path: Path, index: faiss.Index):
    print(f"[ingest] Reading {scene_path.name}...")
    with rasterio.open(scene_path) as src:
        tags = src.tags()
        scene_id = tags["SCENE_ID"]
        offset = int(tags.get("BOA_ADD_OFFSET", 0))
        h, w = src.height, src.width
        
        # We read the whole scene (it's a small AOI chip). For larger ops, we'd read blocks.
        stack_dn = src.read()
        
    scl = stack_dn[quality.BAND_INDEX["scl"]]
    refl = quality.to_reflectance(stack_dn[:5], offset)
    
    # Write scene to DB
    conn = db.get_connection()
    conn.execute(
        "INSERT INTO scenes (scene_id, datetime, platform, cloud_cover, mgrs_tile) VALUES (?, ?, ?, ?, ?)",
        (scene_id, tags.get("ACQUISITION_DATETIME"), tags.get("PLATFORM"), float(tags.get("CLOUD_COVER", 0)), tags.get("MGRS_TILE"))
    )

    t_px = config.TILE_PX
    tiles_to_embed = []
    tile_meta = []
    
    for row in range(0, h - t_px + 1, t_px):
        for col in range(0, w - t_px + 1, t_px):
            r_slice = np.s_[row:row+t_px, col:col+t_px]
            scl_tile = scl[r_slice]
            refl_tile = refl[:, row:row+t_px, col:col+t_px]
            
            stats = quality.tile_stats(refl_tile, scl_tile)
            
            # Save the true-colour chip for the UI
            rgb8 = quality.to_rgb8(refl_tile, scl_tile)
            chip_img = Image.fromarray(rgb8)
            chip_img.save(config.CHIPS_DIR / f"{scene_id}_{row}_{col}.png")
            
            tile_id = f"{scene_id}_{row}_{col}"
            
            # Skip embedding if it's too cloudy or has nodata, but DO record it in the DB 
            # so the time-series knows there was an observation here, it was just bad quality.
            can_embed = stats["valid_frac"] >= config.MIN_VALID_FRAC
            if can_embed:
                tiles_to_embed.append(chip_img)
                tile_meta.append((tile_id, row, col, stats))
            else:
                conn.execute(
                    """INSERT INTO tiles (tile_id, scene_id, row, col, valid_frac, cloud_frac, faiss_id)
                       VALUES (?, ?, ?, ?, ?, ?, NULL)""",
                    (tile_id, scene_id, row, col, stats["valid_frac"], stats["cloud_frac"])
                )

    if not tiles_to_embed:
        print(f"[ingest] {scene_id} had 0 usable tiles.")
        return

    # Embed and add to FAISS
    start_id = index.ntotal
    print(f"[ingest] Embedding {len(tiles_to_embed)} tiles...")
    embeddings = embed.embed_images(tiles_to_embed)
    
    faiss_ids = np.arange(start_id, start_id + len(embeddings), dtype=np.int64)
    index.add(embeddings)
    
    # Write to DB
    rows = []
    for (tile_id, row, col, st), fid in zip(tile_meta, faiss_ids):
        rows.append((
            tile_id, scene_id, row, col,
            st["valid_frac"], st["cloud_frac"],
            st["ndvi"], st["ndwi"], st["ndbi"],
            st["frac_veg"], st["frac_water"], st["frac_built"], st["brightness"],
            int(fid)
        ))
        
    conn.executemany(
        """INSERT INTO tiles (
            tile_id, scene_id, row, col, valid_frac, cloud_frac,
            ndvi, ndwi, ndbi, frac_veg, frac_water, frac_built, brightness, faiss_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        rows
    )
    print(f"[ingest] {scene_id} done.")

def run():
    db.init_db()
    index = load_index()
    done = db.get_ingested_scenes()
    
    tiffs = sorted(config.ARCHIVE_DIR.glob("*.tif"))
    todo = [t for t in tiffs if t.stem not in done]
    
    print(f"[ingest] Found {len(tiffs)} scenes, {len(todo)} need ingestion.")
    if not todo:
        return
        
    t0 = time.time()
    for path in todo:
        ingest_scene(path, index)
        
    faiss.write_index(index, str(config.FAISS_PATH))
    t1 = time.time()
    print(f"[ingest] Complete in {t1-t0:.1f}s. Total vectors: {index.ntotal}")

if __name__ == "__main__":
    run()
