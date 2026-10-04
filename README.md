# GAIA (Geospatial Artificial Intelligence Assistant)

**GAIA** is an advanced, agentic vision-language assistant for remote-sensing imagery. It provides real-time visual question answering (VQA), bi-temporal change detection, and large-scale offline semantic search capabilities over satellite data.

## Features

- **GAIA Cloud (VLM Engine)**: A powerful natural language interface that allows you to chat with your satellite imagery. Ask questions, detect objects, or compare two images (before & after) to identify precise structural changes.
- **GAIA Offline (Archive Mode)**: A fully air-gapped, local retrieval system powered by FAISS and a lightweight vision transformer. Instantly search through thousands of historical tiles using natural language or image-to-image similarity.
- **Automated Change Scanning**: The offline archive autonomously scans your historical geospatial data to surface statistically significant baseline deviations (e.g., newly built structures, water area loss, deforestation).
- **Auto-Ingestion Pipeline**: Any imagery uploaded during an active Cloud session is automatically stretched, chipped, embedded, and added to the offline SQLite/FAISS archive without manual intervention.
- **Native GeoTIFF Support**: Built-in decoders handle complex 16-bit, multi-band GeoTIFFs (like raw Sentinel-2 data) directly, generating normalized previews on-the-fly for the browser.

## Architecture

* **Frontend**: React, TypeScript, Vite, Tailwind CSS (HUD interface)
* **Backend API**: FastAPI, Python
* **Vector Index**: FAISS (Facebook AI Similarity Search)
* **Embeddings**: Local PyTorch execution of `RemoteCLIP-ViT-B-32`
* **Metadata Store**: SQLite

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python 3.10+
- `pip`

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Unix:
# source venv/bin/activate

pip install -r requirements.txt
```

Start the API server:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. Frontend Setup

In a new terminal window:
```bash
cd frontend-code
npm install
npm run dev
```

The application will be available at `http://localhost:5173`. 

## Modes of Operation

Use the global toggle at the top of the interface to switch contexts:
- **CLOUD**: Interactive chat and perception analysis.
- **OFFLINE**: Search the archive and review automated change candidates in an air-gapped environment.
