# Index-Build and Incremental-Ingestion Procedure

This document provides step-by-step instructions to build the GAIA Offline vector index from scratch and to append new imagery incrementally without requiring a full rebuild.

## 1. Building the Index from Scratch

To initialize a completely new offline archive:

### Step 1.1: Clear Existing Data
If you are starting fresh, ensure that the previous index and database files are removed:
```bash
# From the project root
rm -f data/store/archive.sqlite
rm -f data/store/index.faiss
rm -rf data/chips/*
```
*(Note: Paths depend on your `sentinel_index.config` settings, but generally point to the `data/` or `storage/` directories).*

### Step 1.2: Stage the Imagery
Place all of your raw 16-bit, multi-band GeoTIFF scenes into the designated archive staging directory:
```bash
# Example
cp /path/to/raw/sentinel-2/*.tif data/archive/
```

### Step 1.3: Run the Batch Ingestion Pipeline
Execute the Python ingest module. The script will automatically initialize the SQLite tables, create a new FAISS `IndexFlatIP`, and begin iterating through the staged `.tif` files.

```bash
python -m sentinel_index.ingest
```

During this process, the pipeline will:
1. Read the GeoTIFF using `rasterio`.
2. Extract sub-tiles (chips) based on the configured stride.
3. Calculate radiometric indices (NDVI, NDWI, etc.) and cloud cover fractions.
4. Pass valid tiles through the local `RemoteCLIP-ViT-B-32` model to generate embeddings.
5. Save the 8-bit PNG chips for frontend rendering.
6. Commit the vectors to FAISS and the metadata to SQLite.

---

## 2. Incremental Ingestion (Adding New Imagery)

You can add new imagery to an existing, live database without rebuilding the index from scratch. GAIA supports two methods for incremental ingestion:

### Method A: Automated Auto-Ingestion (Via UI)
The easiest way to incrementally append data is through the GAIA Cloud web interface.

1. Launch the backend server and frontend HUD.
2. In the GAIA Cloud dashboard, upload a new `.tif` or `.png` file.
3. **Behind the scenes:** The FastAPI `upload` endpoint automatically triggers a background task (`ingest_user_upload`). 
4. The system instantly processes the uploaded image, generates an embedding, appends it directly to the live FAISS index and SQLite database, and flushes the index to disk. The image is immediately available in the Offline Archive for vector search.

### Method B: Batch Incremental Update (Via CLI)
If you receive a new batch of raw satellite data and wish to ingest it in bulk without using the web UI:

1. Drop the new `.tif` files into the same staging directory (`data/archive/`).
2. Run the ingestion pipeline again:
   ```bash
   python -m sentinel_index.ingest
   ```
3. The script compares the files in the directory against the `scenes` table in the SQLite database. It will **skip** all previously ingested files and only process, embed, and append the new scenes to the existing FAISS index.
