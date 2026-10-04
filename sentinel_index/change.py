"""
Multi-Temporal Change Analysis (PS 2.2.2 & 2.2.3)
Identifies robust, persistent changes in the tile time series.
"""
from __future__ import annotations

from . import db

# Thresholds for change magnitude
NDVI_DROP_THRESH = 0.15     # clearance / construction
NDBI_RISE_THRESH = 0.10     # construction
NDWI_RISE_THRESH = 0.20     # flooding / water expansion
COSINE_DIST_THRESH = 0.85   # semantic embedding change (requires FAISS)


class ChangeEngine:
    def __init__(self):
        self.conn = db.get_connection()
        
    def _fetch_timeseries(self, row: int, col: int) -> list[dict]:
        query = """
            SELECT t.*, s.datetime
            FROM tiles t
            JOIN scenes s ON t.scene_id = s.scene_id
            WHERE t.row = ? AND t.col = ? AND t.valid_frac >= 0.80
            ORDER BY s.datetime ASC
        """
        return [dict(r) for r in self.conn.execute(query, (row, col))]

    def analyze_tile(self, row: int, col: int) -> dict | None:
        """
        Walks the timeline of a single cell to find persistent change.
        Returns change metadata or None if stable.
        """
        ts = self._fetch_timeseries(row, col)
        if len(ts) < 3:
            return None  # not enough history

        # Simple baseline: take the median of the first 2 clear observations
        base_ndvi = sum(obs["ndvi"] for obs in ts[:2]) / 2.0
        base_ndbi = sum(obs["ndbi"] for obs in ts[:2]) / 2.0
        base_ndwi = sum(obs["ndwi"] for obs in ts[:2]) / 2.0
        
        # Look for the first observation that triggers a change and PERSISTS
        # in the subsequent observation (false-alarm suppression, PS 2.2.3).
        for i in range(2, len(ts) - 1):
            obs = ts[i]
            obs_next = ts[i+1]
            
            d_ndvi = obs["ndvi"] - base_ndvi
            d_ndbi = obs["ndbi"] - base_ndbi
            d_ndwi = obs["ndwi"] - base_ndwi
            
            # Check persistence
            d_ndvi_next = obs_next["ndvi"] - base_ndvi
            d_ndbi_next = obs_next["ndbi"] - base_ndbi
            d_ndwi_next = obs_next["ndwi"] - base_ndwi

            change_type = None
            
            # 1. Construction / Development (Vegetation clears, Built-up rises)
            if (d_ndvi < -0.05 and d_ndbi > 0.02) and (d_ndvi_next < -0.05 and d_ndbi_next > 0.02):
                change_type = "construction"
                
            # 2. Water variation (Water index rises significantly)
            elif (d_ndwi > 0.05) and (d_ndwi_next > 0.05):
                change_type = "water_expansion"
                
            # 3. Clearance (Vegetation drops, but not necessarily built)
            elif (d_ndvi < -0.05) and (d_ndvi_next < -0.05):
                change_type = "clearance"
                
            # 4. Generic anomaly (catch-all for demo purposes)
            elif abs(d_ndvi) > 0.05 and abs(d_ndvi_next) > 0.05:
                change_type = "vegetation_anomaly"
                
            if change_type:
                # Calculate simple confidence based on magnitude
                conf = min(1.0, max(abs(d_ndvi) / 0.3, abs(d_ndbi) / 0.2, abs(d_ndwi) / 0.4))
                
                return {
                    "type": change_type,
                    "row": row,
                    "col": col,
                    "confidence": conf,
                    "earliest_date": obs["datetime"],     # PS 2.2.2 "earliest available observation"
                    "baseline_date": ts[1]["datetime"],
                    "evidence": {
                        "before_tile": ts[1]["tile_id"],
                        "after_tile": obs["tile_id"],
                        "delta_ndvi": d_ndvi,
                        "delta_ndbi": d_ndbi,
                        "delta_ndwi": d_ndwi
                    }
                }
        return None

    def find_all_changes(self) -> list[dict]:
        """Scans all unique spatial cells for changes."""
        cells = self.conn.execute("SELECT DISTINCT row, col FROM tiles").fetchall()
        changes = []
        for r in cells:
            res = self.analyze_tile(r["row"], r["col"])
            if res:
                changes.append(res)
        return sorted(changes, key=lambda c: c["confidence"], reverse=True)
