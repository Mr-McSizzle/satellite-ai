# GAIA System Architecture

This document provides a written description of the system design for the GAIA (Geospatial Artificial Intelligence Assistant) platform, fulfilling the requirement for the Architecture Note.

## High-Level Architecture

GAIA operates via a decoupled client-server model, unified by a single FastAPI gateway that multiplexes between two operational environments:

1.  **GAIA Cloud (VLM Engine)**: A real-time, interactive Vision-Language Model interface for ad-hoc intelligence querying.
2.  **GAIA Offline (Archive Mode)**: A completely localized, air-gapped vector search and automated change scanning system.

### 1. Presentation Layer (Frontend)
-   **Framework**: React 18, Vite, TypeScript, and Tailwind CSS.
-   **Design Pattern**: The HUD (Heads-Up Display) dashboard uses a global state toggle to switch between the Cloud and Offline perspectives seamlessly without reloading the client context.
-   **Image Previews**: Because standard browsers cannot render 16-bit multi-band GeoTIFFs, the frontend relies on the backend to dynamically generate and serve down-sampled 8-bit PNG previews for rendering uploaded satellite data.

### 2. Application Gateway (FastAPI Backend)
-   **Framework**: Python FastAPI running on Uvicorn.
-   **Routing**:
    -   `/api/v1/*`: Handles Cloud VLM interactions, including image uploading, processing, and chat sessions.
    -   `/offline/api/v1/*`: Proxies requests to the local Sentinel Index, enabling vector search, retrieval, and batch change scanning.
-   **Background Tasks**: The backend leverages FastAPI's background tasks to bridge the two modes: whenever an image is uploaded for Cloud analysis, a background task automatically triggers the ingestion pipeline to chip, embed, and index the imagery into the Offline archive.

### 3. Perception Engine (Cloud Mode)
-   **Capabilities**: Supports Single-Image Visual Question Answering (VQA) and Bi-Temporal Change VQA.
-   **Resilience**: The controller implements a fallback cascade. If a model rejects a schema or tool combination, the adapter safely degrades to a simpler prompt strategy or falls back to a backup model, ensuring continuous operation.
-   **Image Normalization**: Raw 16-bit GeoTIFF arrays (e.g., Sentinel-2 L2A) are stretched dynamically via `rasterio` into standard tensors, preventing the silent perception failures that occur when standard image decoders attempt to parse 16-bit scientific data.

### 4. Vector Retrieval & Index (Offline Mode)
The Offline mode operates entirely on local hardware, requiring no external network calls.
-   **Feature Extraction**: Tiles are embedded using a local PyTorch inference of `RemoteCLIP-ViT-B-32`.
-   **Vector Index**: Vector embeddings are normalized and pushed into a **FAISS** `IndexFlatIP` (Inner Product) index, allowing for blazing-fast cosine similarity searches.
-   **Metadata Store**: A local **SQLite** database stores relational metadata, including scene telemetry (platform, acquisition datetime), tile metrics (cloud fraction, valid fraction), and calculated radiometric indices (NDVI, NDWI, NDBI).
-   **Change Scanner**: The scanner iterates through the SQLite timeline for each geospatial tile (MGRS block), comparing historical baselines against the latest observations to highlight statistically significant deviations in radiometric signatures.

## Data Flow Diagram (Summary)

```
[User Interface] 
      │ (Upload GeoTIFF / Query)
      ▼
[FastAPI Gateway]
      │
      ├─► (If /api/v1/analyze) ──► [GAIA Perception Engine] ──► (Generates Answer)
      │
      ├─► (Background Task)    ──► [Auto-Ingestion Pipeline]
      │                                   │ (Rasterio stretch, clip, 8-bit chip)
      │                                   ▼
      │                            [RemoteCLIP-ViT-B-32] ──► (Generate Embeddings)
      │                                   │
      │                                   ▼
      │                            [ FAISS + SQLite ]
      │
      └─► (If /offline/api/v1) ──► [Local Search/Change Scanner] ──► (Queries DB/FAISS)
```
