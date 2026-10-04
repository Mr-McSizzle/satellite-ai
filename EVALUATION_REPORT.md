# PS 26227: Reproducible Evaluation Report

This document fulfills the Phase 6 reporting requirements and Section 2.3 of the Problem Statement, detailing the performance, footprint, and hardware constraints of the offline evaluation system.

## 1. Hardware Profile
- **Environment**: Local on-premises deployment, network isolated.
- **CPU**: (Standard Laptop CPU)
- **GPU**: NVIDIA GeForce RTX 3050 Laptop GPU
- **VRAM**: 4096 MiB (4 GB)
- **Constraint Met**: The entire ingestion, embedding, and semantic retrieval pipeline runs comfortably within the 4 GB VRAM limit. 

## 2. Dataset & Indexing Profile
The evaluation dataset consists of a multi-temporal stack over Navi Mumbai (MGRS Tile 43QBA).
- **Number of Scenes (GeoTIFFs)**: 14 Sentinel-2 L2A acquisitions (2019–2025).
- **Raw Scene Storage**: 16.4 MB
- **Total Tiles Extracted (64x64px @ 10m)**: 1,694
- **Valid Tiles (Cloud/Shadow filtered)**: 330
- **Total Indexed Area**: ~13.5 sq km of usable clear observations across the time series.

## 3. Storage Footprint
The offline index is designed to be highly compressed and append-only.
- **SQLite Metadata Database** (`archive.sqlite`): 389 KB (Stores temporal stats, thematic fractions, and review queue).
- **FAISS Vector Index** (`tiles.faiss`): 675 KB (Stores 512-dimensional normalized float32 vectors).
- **UI Chip Cache** (`chips/*.png`): 1.7 MB (Small RGB representations for analyst review).
- **Total Index Overhead**: ~2.7 MB (Approx. 16% overhead relative to the raw imagery).

## 4. Performance & Latency
- **Ingestion & Build Time**: 10.1 seconds to tile, mask, calculate spectral indices, run the RemoteCLIP embedder on GPU, and persist 14 scenes.
- **Search Query Latency (Text & Image)**: < 50ms per query (FAISS Inner Product search).
- **Change Scan Latency**: < 100ms to scan the entire SQLite index and construct persistent change events across the time series.

## 5. Offline Capabilities Demonstrated
- **Incremental Ingest (PS 2.2.6)**: Adding a new `.tif` file to the archive directory and re-running `ingest.py` appends to FAISS and SQLite without a full rebuild.
- **Semantic Retrieval (PS 2.2.1)**: Powered by local ViT-B/32 RemoteCLIP weights loaded directly from disk.
- **Multi-Temporal Change (PS 2.2.2 & 2.2.3)**: Handled via `change.py` walking the temporal stack. Identifies construction, water variation, and clearance, calculating confidence via NDBI/NDVI/NDWI index deltas and suppressing false alarms by requiring persistence across ≥2 observations.
- **Analyst Audit Trail (PS 2.2.5)**: The UI review queue pushes confirmed/rejected decisions to `archive.sqlite`.
