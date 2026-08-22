from fastapi.testclient import TestClient

def test_analyze_single_image_vqa(client: TestClient) -> None:
    """Test SINGLE_IMAGE_VQA task classification and response structure."""
    payload = {
        "query": "What is the building in the center?",
        "image_paths": ["/data/img1.png"]
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["task"] == "SINGLE_IMAGE_VQA"
    assert "single image" in data["answer"].lower()
    assert data["confidence"] == 0.85
    assert data["evidence"] == []
    assert len(data["trace"]) == 2
    assert data["trace"][0]["result"] == "SINGLE_IMAGE_VQA"
    assert data["trace"][1]["result"] == "mock_vqa_tool"

def test_analyze_change_vqa(client: TestClient) -> None:
    """Test CHANGE_VQA task classification and response structure."""
    payload = {
        "query": "Show me what changed between these dates.",
        "image_paths": ["/data/img1.png", "/data/img2.png"]
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["task"] == "CHANGE_VQA"
    assert "change" in data["answer"].lower()
    assert data["trace"][0]["result"] == "CHANGE_VQA"
    assert data["trace"][1]["result"] == "mock_change_tool"

def test_analyze_grounding(client: TestClient) -> None:
    """Test GROUNDING task classification and response structure."""
    payload = {
        "query": "Where is the vegetation area?",
        "image_paths": ["/data/img1.png"]
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["task"] == "GROUNDING"
    assert len(data["evidence"]) == 1
    assert data["evidence"][0]["label"] == "grounded_area"
    assert data["trace"][0]["result"] == "GROUNDING"
    assert data["trace"][1]["result"] == "mock_grounding_tool"

def test_analyze_fusion(client: TestClient) -> None:
    """Test OPTICAL_SAR_FUSION task classification and response structure."""
    payload = {
        "query": "Analyze using SAR data.",
        "image_paths": ["/data/img_optical.png", "/data/img_sar.png"]
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["task"] == "OPTICAL_SAR_FUSION"
    assert "fused" in data["answer"].lower()
    assert data["trace"][0]["result"] == "OPTICAL_SAR_FUSION"
    assert data["trace"][1]["result"] == "mock_fusion_tool"

def test_analyze_invalid_empty_query(client: TestClient) -> None:
    """Test validation errors for empty/whitespace query."""
    # Empty query string
    payload1 = {
        "query": "",
        "image_paths": ["/data/img1.png"]
    }
    response1 = client.post("/api/v1/analyze", json=payload1)
    assert response1.status_code == 422

    # Whitespace only query
    payload2 = {
        "query": "    ",
        "image_paths": ["/data/img1.png"]
    }
    response2 = client.post("/api/v1/analyze", json=payload2)
    assert response2.status_code == 422

def test_analyze_invalid_empty_image_paths(client: TestClient) -> None:
    """Test validation errors for empty image paths list."""
    payload = {
        "query": "Describe this image.",
        "image_paths": []
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 422
