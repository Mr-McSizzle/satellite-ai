# Architecture & Provenance (PS 26227)

## 1. System Architecture
The offline system replaces external cloud dependencies with local data structures:
1. **rasterio** handles spatial coordinates, bounds, and radiometric arrays (handling the Jan 2022 Copernicus baseline BOA shift).
2. **FAISS** provides L2-normalized Inner Product vector retrieval for semantic search and clustering.
3. **SQLite** manages relational metadata (dates, thematic fractions like NDVI, and analyst decisions).
4. **FastAPI** serves the retrieval and change-detection endpoints locally.
5. **React/Vite** provides the analyst UI.

## 2. Model & Weights Provenance (PS 2.2.7)

### RemoteCLIP (Semantic Embedder)
- **Architecture**: ViT-B/32 (Vision Transformer Base, 32x32 patch size).
- **Function**: Aligns natural language text queries with remote sensing imagery in a shared 512-dimensional vector space.
- **Source**: `RemoteCLIP-ViT-B-32.pt` downloaded from the official repository (originally trained by the authors of "RemoteCLIP: A Vision Language Foundation Model for Remote Sensing").
- **Licence**: Apache 2.0 (Open Source, permissive for commercial and evaluation use).
- **Offline Assurance**: The model is loaded entirely from `models/weights/`. Environment variables `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` are enforced in `config.py`.

## 3. Deployment & Execution Instructions

To replicate the index build and start the system in a network-isolated environment:

1. **Staging (Online Pre-requisite)**
   Run `python -m sentinel_index.stage_data` to download a sample of public Sentinel-2 L2A GeoTIFFs into `data/archive`. 
   *(In a true offline environment, these GeoTIFFs would be provided via external drive and copied to the folder).*

2. **Incremental Ingestion (Offline)**
   Run `python -m sentinel_index.ingest`. This will:
   - Tile the new GeoTIFFs.
   - Run the local RemoteCLIP embedder on the GPU.
   - Append to `data/store/tiles.faiss` and `data/store/archive.sqlite`.

3. **Start API Server (Offline)**
   Run `python -m uvicorn sentinel_index.api:app --host 127.0.0.1 --port 8000`.

4. **Start UI (Offline)**
   Run `cd frontend-code && npm run dev`. Navigate to the provided local URL (e.g., `http://localhost:5173`).
