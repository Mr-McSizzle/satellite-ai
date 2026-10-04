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
        crs_wkt = src.crs.to_wkt() if src.crs else None
        geo_transform = str(src.transform) if src.transform else None
        
    scl = stack_dn[quality.BAND_INDEX["scl"]]
    refl = quality.to_reflectance(stack_dn[:5], offset)
    
    # Write scene to DB
    conn = db.get_connection()
    conn.execute(
        "INSERT INTO scenes (scene_id, datetime, platform, cloud_cover, mgrs_tile, crs, geotransform) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (scene_id, tags.get("ACQUISITION_DATETIME"), tags.get("PLATFORM"), float(tags.get("CLOUD_COVER", 0)), tags.get("MGRS_TILE"), crs_wkt, geo_transform)
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

def ingest_user_upload(img_path: Path, index: faiss.Index = None) -> str:
    """Ingests an arbitrary user upload (PNG/JPG/TIF) into the FAISS offline archive as a single tile."""
    from uuid import uuid4
    import datetime
    
    scene_id = f"UPLOAD_{uuid4().hex[:8]}"
    print(f"[ingest] Ingesting user upload {img_path.name} as {scene_id}...")
    
    # Open image (PNG/JPG/8-bit TIFF/16-bit multi-band GeoTIFF)
    try:
        from sentinel_index.imaging import load_rgb
        img = load_rgb(img_path)
    except Exception as e:
        print(f"[ingest] Failed to read {img_path}: {e}")
        return None
        
    # Resize to something reasonable for CLIP (it takes 224x224 typically, but we use 64x64 chips for visual consistency in UI)
    img_chip = img.resize((config.TILE_PX, config.TILE_PX))
    chip_name = f"{scene_id}_0_0.png"
    img_chip.save(config.CHIPS_DIR / chip_name)
    
    crs_wkt = None
    geo_transform = None
    try:
        import rasterio
        with rasterio.open(img_path) as src:
            if src.crs:
                crs_wkt = src.crs.to_wkt()
            if src.transform:
                geo_transform = str(src.transform)
    except:
        pass
        
    conn = db.get_connection()
    now_str = datetime.datetime.now().isoformat()
    conn.execute(
        "INSERT INTO scenes (scene_id, datetime, platform, cloud_cover, mgrs_tile, crs, geotransform) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (scene_id, now_str, "USER_UPLOAD", 0.0, "USER", crs_wkt, geo_transform)
    )
    
    # Embed and add to FAISS
    if index is None:
        index = load_index()
        
    start_id = index.ntotal
    emb = embed.embed_images([img_chip])
    index.add(emb)
    
    tile_id = f"{scene_id}_0_0"
    conn.execute(
        """INSERT INTO tiles (
            tile_id, scene_id, row, col, valid_frac, cloud_frac,
            ndvi, ndwi, ndbi, frac_veg, frac_water, frac_built, brightness, faiss_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (tile_id, scene_id, 0, 0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, int(start_id))
    )
    
    # Flush index if we loaded it here
    faiss.write_index(index, str(config.FAISS_PATH))
    
    # Reload search engine singleton if it's imported (to reflect new data)
    import sys
    if "sentinel_index.api" in sys.modules:
        api = sys.modules["sentinel_index.api"]
        if api.engine_search is not None:
            api.engine_search.reload()
        
    return tile_id

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
