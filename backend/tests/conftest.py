import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add the 'backend' root directory to python path so 'app' can be imported properly during testing
backend_root = str(Path(__file__).resolve().parent.parent)
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.main import app

@pytest.fixture(scope="module")
def client() -> TestClient:
    """Fixture that returns a TestClient instance for testing endpoints."""
    with TestClient(app) as c:
        yield c
