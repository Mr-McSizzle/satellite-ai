# Model and Dataset Provenance

This document outlines the origins, licenses, and packaging of the machine learning models and datasets utilized by the GAIA system.

## 1. Models

### RemoteCLIP-ViT-B-32
* **Purpose**: Generates vector embeddings for tiles in the GAIA Offline Archive to facilitate semantic search and anomaly detection.
* **Origin**: Developed and open-sourced by the researchers behind RemoteCLIP, a vision-language foundation model tailored specifically for remote sensing data.
* **License**: MIT License / Apache 2.0.
* **Packaged Weights**: The model weights are packaged locally within the repository to ensure air-gapped functionality. They are located at: `models/weights/RemoteCLIP-ViT-B-32.pt`.

### GAIA Cloud VLM Engine
* **Purpose**: Performs high-level visual question answering (VQA) and bi-temporal change reasoning via the Cloud interface.
* **Origin**: Proprietary cloud-hosted Vision-Language Model endpoint, accessed securely via the unified controller adapter.
* **License**: Commercial API Terms of Service.
* **Packaged Weights**: Not applicable; accessed dynamically over HTTPS via the controller API.

---

## 2. Datasets

### Offline Archive Seed Data (Sentinel-2)
* **Purpose**: Historical baseline scenes used to populate the initial FAISS vector index and SQLite timeline for change scanning.
* **Source**: Raw `.tif` files sourced from the European Space Agency's (ESA) Copernicus Open Access Hub (Sentinel-2 L2A optical imagery).
* **License**: Copernicus Sentinel Data is open, free, and available under a liberal use policy (equivalent to CC BY 4.0).

### Evaluation / Test Imagery
* **Purpose**: E2E smoke tests and validation scenes (e.g., `test1.tif`, `test2.tif`).
* **Source**: User-provided geospatial data.
* **License**: Project-specific / Proprietary user data.
