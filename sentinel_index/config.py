"""Central configuration. All paths are local; nothing here requires network access."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("SI_DATA_DIR", ROOT / "data"))
ARCHIVE_DIR = DATA_DIR / "archive"          # input GeoTIFF / COG scenes
STORE_DIR = DATA_DIR / "store"              # index + db + chips (derived, rebuildable)
CHIPS_DIR = STORE_DIR / "chips"
DB_PATH = STORE_DIR / "archive.sqlite"
FAISS_PATH = STORE_DIR / "tiles.faiss"
WEIGHTS_DIR = ROOT / "models" / "weights"

# Embedding model (RemoteCLIP, Apache-2.0, https://github.com/ChenDelong1999/RemoteCLIP)
CLIP_ARCH = "ViT-B-32"
CLIP_WEIGHTS = WEIGHTS_DIR / "RemoteCLIP-ViT-B-32.pt"
EMBED_DIM = 512

# Tiling: 64 px at 10 m = 640 m tiles on a fixed per-scene grid. Because all scenes of an
# AOI share one MGRS grid, (row, col) identifies the same ground cell across time.
TILE_PX = 64
MIN_VALID_FRAC = 0.80   # tiles below this usable-pixel fraction are kept but flagged unusable

# Reflectance -> 8-bit display/embedding stretch. A FIXED stretch (not per-image) keeps
# appearance comparable across dates, which matters for both retrieval and change.
STRETCH_MAX_REFL = 0.30
GAMMA = 1 / 1.4

PIPELINE_VERSION = "si-0.1.0"

for d in (ARCHIVE_DIR, STORE_DIR, CHIPS_DIR, WEIGHTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Enforce offline model loading for HF/transformers if anything tries.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
