"""
Semantic Retrieval Engine (PS 2.2.1)
Combines FAISS vector similarity with SQLite metadata filtering.
"""
from __future__ import annotations

import faiss
import numpy as np

from . import config, db, embed


class SearchEngine:
    def __init__(self):
        self.index = None
        self.conn = db.get_connection()
        self.reload()

    def reload(self):
        if config.FAISS_PATH.exists():
            self.index = faiss.read_index(str(config.FAISS_PATH))
            print(f"[search] Loaded FAISS index with {self.index.ntotal} vectors.")
        else:
            self.index = faiss.IndexFlatIP(config.EMBED_DIM)

    def _get_metadata(self, faiss_ids: np.ndarray, distances: np.ndarray) -> list[dict]:
        """Join FAISS results with SQLite metadata."""
        if len(faiss_ids) == 0:
            return []
            
        placeholders = ",".join("?" * len(faiss_ids))
        query = f"""
            SELECT t.*, s.datetime, s.platform
            FROM tiles t
            JOIN scenes s ON t.scene_id = s.scene_id
            WHERE t.faiss_id IN ({placeholders})
        """
        rows = {r["faiss_id"]: dict(r) for r in self.conn.execute(query, tuple(faiss_ids.tolist()))}
        
        results = []
        for fid, dist in zip(faiss_ids.tolist(), distances.tolist()):
            if fid not in rows:
                continue
            r = rows[fid]
            # format the chip path relative to the store so the frontend can load it
            chip_url = f"/api/v1/tiles/chip/{r['scene_id']}_{r['row']}_{r['col']}.png"
            results.append({
                "tile_id": r["tile_id"],
                "scene_id": r["scene_id"],
                "datetime": r["datetime"],
                "score": float(dist),
                "chip_url": chip_url,
                "row": r["row"],
                "col": r["col"],
                "cloud_frac": r["cloud_frac"],
                "frac_veg": r["frac_veg"],
                "frac_water": r["frac_water"],
                "frac_built": r["frac_built"],
            })
        return results

    def text_search(self, text: str, k: int = 20) -> list[dict]:
        if self.index.ntotal == 0:
            return []
        q_vec = embed.embed_text([text])
        distances, indices = self.index.search(q_vec, k)
        return self._get_metadata(indices[0], distances[0])

    def image_search(self, tile_id: str, k: int = 20) -> list[dict]:
        """Find tiles similar to the given tile (PS 2.2.4 clustering primitive)."""
        row = self.conn.execute("SELECT faiss_id FROM tiles WHERE tile_id = ?", (tile_id,)).fetchone()
        if not row or row["faiss_id"] is None:
            raise ValueError(f"Tile {tile_id} has no embedding.")
            
        # Reconstruct vector from FAISS
        q_vec = np.empty((1, config.EMBED_DIM), dtype=np.float32)
        self.index.reconstruct(row["faiss_id"], q_vec[0])
        
        distances, indices = self.index.search(q_vec, k + 1)
        
        # Filter out the query itself
        mask = indices[0] != row["faiss_id"]
        return self._get_metadata(indices[0][mask][:k], distances[0][mask][:k])
