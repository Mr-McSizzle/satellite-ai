# SatQuery AI Backend

This is the initial FastAPI-based backend framework for the SatQuery AI (SIH) project.

## Directory Structure

```text
backend/
├── app/
│   ├── main.py              # Application entry point, CORS configuration, lifespan, and router mounting
│   ├── api/
│   │   ├── endpoints/       # Route handlers
│   │   │   └── health.py    # Health check endpoint
│   │   └── router.py        # Centralized router combining endpoints
│   ├── schemas/             # Pydantic schemas for data validation and serialization
│   │   └── health.py        # Health response Pydantic schema
│   ├── services/            # Placeholder for agentic controller and external VLM integration
│   ├── tools/               # Placeholder for remote sensing algorithms and utility tools
│   └── core/
│       ├── config.py        # App configuration settings using Pydantic Settings
│       └── logging_config.py# Centralized standard logging setup
│
├── tests/
│   ├── conftest.py          # Pytest setup and shared TestClient fixture
│   └── test_health.py       # Health check API unit tests
│
├── requirements.txt         # Project dependencies
└── README.md                # Development instructions
```

## Setup & Installation

### 1. Create a Python Virtual Environment
Ensure your terminal is in the `backend` directory:
```bash
cd backend
```

Create a virtual environment (Python 3.10+ recommended):
```bash
python -m venv venv
```

### 2. Activate the Virtual Environment
- **On Windows (cmd):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **On Windows (PowerShell):**
  ```powershell
  venv\Scripts\activate.ps1
  ```
- **On macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Running the Server

Start the development server using Uvicorn (ensure your working directory is the `backend` folder):
```bash
uvicorn app.main:app --reload
```

By default, the server will start at `http://127.0.0.1:8000`. You can view the interactive OpenAPI documentation at `http://127.0.0.1:8000/docs`.

---

## Testing

### Automated Tests
Run the unit test suite using Pytest from the `backend` directory:
```bash
pytest
```

### Manual Testing
To manually verify the health check endpoint, perform a GET request:

- **Using Curl:**
  ```bash
  curl http://127.0.0.1:8000/health
  ```
- **Using a Web Browser:**
  Navigate to `http://127.0.0.1:8000/health`

**Expected Response:**
```json
{
  "status": "ok",
  "service": "satquery-backend"
}
```
