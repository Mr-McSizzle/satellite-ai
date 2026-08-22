"""
Integration tests for POST /api/v1/analyze.

These tests exercise the full stack:
    TestClient → FastAPI endpoint → AnalysisService → GaiaAdapter → GaiaController
    → MockVLM / MockPrithvi

All image references must be .tif or .tiff (validated by schema).
"""
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _optical(ref: str) -> dict:
    return {"reference": ref, "modality": "optical"}

def _sar(ref: str) -> dict:
    return {"reference": ref, "modality": "SAR"}


# ---------------------------------------------------------------------------
# Health (smoke test — must still pass)
# ---------------------------------------------------------------------------

def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "satquery-backend"


# ---------------------------------------------------------------------------
# Single-image VQA
# ---------------------------------------------------------------------------

def test_analyze_single_image_vqa(client: TestClient) -> None:
    """VQA query with one optical image — GAIA should classify as 'vqa'."""
    payload = {
        "query": "Is there water in this image?",
        "images": [_optical("/data/scene.tif")],
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["status"] == "success"
    assert data["task"] == "vqa"
    assert isinstance(data["answer"], str) and data["answer"]
    assert isinstance(data["confidence"], float)
    assert "execution_trace" in data
    assert data["execution_trace"]["execution_status"] == "success"
    # VQA uses only VLM — one tool invoked
    tools = data["execution_trace"]["tools_invoked"]
    assert len(tools) == 1
    assert tools[0]["tool_name"] == "vlm"


# ---------------------------------------------------------------------------
# Grounding
# ---------------------------------------------------------------------------

def test_analyze_grounding(client: TestClient) -> None:
    """Grounding query — GAIA should classify as 'grounding'."""
    payload = {
        "query": "Highlight the water body in the image.",
        "images": [_optical("/data/scene.tif")],
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["status"] == "success"
    assert data["task"] == "grounding"
    tools = data["execution_trace"]["tools_invoked"]
    assert any(t["tool_name"] == "vlm" for t in tools)


# ---------------------------------------------------------------------------
# Change VQA
# ---------------------------------------------------------------------------

def test_analyze_change_vqa(client: TestClient) -> None:
    """Change-detection query with two optical images — GAIA → 'change_vqa'."""
    payload = {
        "query": "What changed between these two images?",
        "images": [
            _optical("/data/before.tif"),
            _optical("/data/after.tif"),
        ],
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["status"] == "success"
    assert data["task"] == "change_vqa"
    tools = data["execution_trace"]["tools_invoked"]
    tool_names = [t["tool_name"] for t in tools]
    assert "prithvi" in tool_names
    assert "vlm" in tool_names


# ---------------------------------------------------------------------------
# Optical-SAR fusion
# ---------------------------------------------------------------------------

def test_analyze_optical_sar_fusion(client: TestClient) -> None:
    """Fusion query with optical + SAR — GAIA → 'optical_sar_fusion'."""
    payload = {
        "query": "Use the optical and SAR images together.",
        "images": [
            _optical("/data/optical.tif"),
            _sar("/data/sar.tif"),
        ],
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["status"] == "success"
    assert data["task"] == "optical_sar_fusion"
    tools = data["execution_trace"]["tools_invoked"]
    tool_names = [t["tool_name"] for t in tools]
    assert "prithvi" in tool_names
    assert "vlm" in tool_names


# ---------------------------------------------------------------------------
# execution_trace structure
# ---------------------------------------------------------------------------

def test_execution_trace_structure(client: TestClient) -> None:
    """Verify execution_trace contains the required GAIA contract fields."""
    payload = {
        "query": "Describe this scene.",
        "images": [_optical("/data/scene.tif")],
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200, response.text
    trace = response.json()["execution_trace"]

    assert "task_selected" in trace
    assert "execution_status" in trace
    assert "tools_invoked" in trace
    assert "validation_result" in trace
    assert "audit" in trace


# ---------------------------------------------------------------------------
# Validation errors — 422
# ---------------------------------------------------------------------------

def test_invalid_empty_query(client: TestClient) -> None:
    """Empty query must be rejected with HTTP 422."""
    payload = {"query": "", "images": [_optical("/data/scene.tif")]}
    assert client.post("/api/v1/analyze", json=payload).status_code == 422

def test_invalid_whitespace_query(client: TestClient) -> None:
    """Whitespace-only query must be rejected with HTTP 422."""
    payload = {"query": "   ", "images": [_optical("/data/scene.tif")]}
    assert client.post("/api/v1/analyze", json=payload).status_code == 422

def test_invalid_no_images(client: TestClient) -> None:
    """Empty images list must be rejected with HTTP 422."""
    payload = {"query": "Describe this scene.", "images": []}
    assert client.post("/api/v1/analyze", json=payload).status_code == 422

def test_invalid_image_format_png(client: TestClient) -> None:
    """PNG extension must be rejected with HTTP 422."""
    payload = {
        "query": "Describe this scene.",
        "images": [{"reference": "/data/scene.png", "modality": "optical"}],
    }
    assert client.post("/api/v1/analyze", json=payload).status_code == 422

def test_invalid_image_format_jpeg(client: TestClient) -> None:
    """JPEG extension must be rejected with HTTP 422."""
    payload = {
        "query": "Describe this scene.",
        "images": [{"reference": "/data/scene.jpg", "modality": "optical"}],
    }
    assert client.post("/api/v1/analyze", json=payload).status_code == 422

def test_invalid_modality(client: TestClient) -> None:
    """Unknown modality must be rejected with HTTP 422."""
    payload = {
        "query": "Describe this scene.",
        "images": [{"reference": "/data/scene.tif", "modality": "unknown"}],
    }
    assert client.post("/api/v1/analyze", json=payload).status_code == 422
