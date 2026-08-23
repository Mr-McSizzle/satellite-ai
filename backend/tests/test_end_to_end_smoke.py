from fastapi.testclient import TestClient
from app.main import app

def test_smoke_end_to_end():
    """
    HTTP request -> backend -> GAIA -> MockVLM -> valid API response
    """
    client = TestClient(app)
    
    payload = {
        "query": "Is there water in this image?",
        "images": [{"reference": "/data/scene.tif", "modality": "optical"}],
    }
    
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "answer" in data
    assert "evidence" in data
    assert "confidence" in data
    assert "execution_trace" in data
    assert data["execution_trace"]["execution_status"] == "success"
    
    # Check it used MockVLM
    tools = data["execution_trace"]["tools_invoked"]
    vlm_tool = next(t for t in tools if t["tool_name"] == "vlm")
    assert vlm_tool["parameters"]["model"] == "mock_vlm"
