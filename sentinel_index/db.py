"""SQLite storage for the offline archive."""
import sqlite3
from typing import Iterator

from . import config


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH, isolation_level=None, check_same_thread=False)
    conn.execute("pragma journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scenes (
            scene_id TEXT PRIMARY KEY,
            datetime TEXT NOT NULL,
            platform TEXT,
            cloud_cover REAL,
            mgrs_tile TEXT,
            bounds_wkt TEXT,
            crs TEXT,                       -- Preservation of Coordinate Reference System
            geotransform TEXT               -- Preservation of Affine Transform
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tiles (
            tile_id TEXT PRIMARY KEY,       -- scene_id + "_" + row + "_" + col
            scene_id TEXT REFERENCES scenes(scene_id),
            row INTEGER,
            col INTEGER,
            lon REAL,                       -- center longitude
            lat REAL,                       -- center latitude
            valid_frac REAL,
            cloud_frac REAL,
            ndvi REAL,
            ndwi REAL,
            ndbi REAL,
            frac_veg REAL,
            frac_water REAL,
            frac_built REAL,
            brightness REAL,
            faiss_id INTEGER,               -- NULL if not embedded (e.g. too cloudy)
            UNIQUE (scene_id, row, col)
        )
    """)
    # Index for fast time-series queries on a specific spatial cell
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tiles_spatial ON tiles(row, col)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tiles_faiss ON tiles(faiss_id)")
    
    # Review queue and audit decisions
    conn.execute("""
        CREATE TABLE IF NOT EXISTS review_queue (
            candidate_id TEXT PRIMARY KEY,
            type TEXT,                      -- 'change' or 'search'
            tile_id TEXT REFERENCES tiles(tile_id),
            score REAL,                     -- embedding distance or confidence
            status TEXT DEFAULT 'pending',  -- 'pending', 'confirmed', 'rejected'
            audit_note TEXT
        )
    """)


def get_ingested_scenes() -> set[str]:
    conn = get_connection()
    return {row[0] for row in conn.execute("SELECT scene_id FROM scenes")}
