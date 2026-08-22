from fastapi.testclient import TestClient

def test_health_check(client: TestClient) -> None:
    """Tests the GET /health endpoint to ensure it returns 200 OK and correct JSON body."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "satquery-backend"
