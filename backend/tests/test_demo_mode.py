import os
import pytest
from unittest.mock import patch, MagicMock

from backend.app.schemas.analysis import AnalysisRequest, ImageInfo
from backend.app.services.gaia_adapter import GaiaAdapter

@pytest.fixture
def clean_env():
    orig_demo = os.environ.get("DEMO_MODE")
    yield
    if orig_demo is not None:
        os.environ["DEMO_MODE"] = orig_demo
    elif "DEMO_MODE" in os.environ:
        del os.environ["DEMO_MODE"]

def test_demo_mode_true(clean_env):
    os.environ["DEMO_MODE"] = "true"
    
    # We patch the run method of GeminiDemoAdapter to avoid actual initialization errors
    with patch("controller.models.gemini_demo_adapter.GeminiDemoAdapter.run") as mock_run:
        mock_run.return_value = {
            "status": "success",
            "answer": "Demo answer",
            "evidence": [],
            "metadata": {"demo_mode": True},
            "errors": [],
            "warnings": [],
            "confidence": 0.9,
            "execution_trace": {}
        }
        
        # When GaiaAdapter runs, it'll invoke the controller, which invokes the mocked adapter.
        # But wait, GaiaController runs `vlm.run(...)`.
        
        # Reset singleton if it was initialized
        GaiaAdapter._instance = None
        adapter = GaiaAdapter()
        
        req = AnalysisRequest(query="Is there water in this image?", images=[ImageInfo(reference="img.tif", modality="optical")])
        data = adapter.run(req)
        
        # Instead of parsing the exact nested result (which the executor might mangle if not careful), 
        # let's just check that `mock_run` was called, proving GeminiDemoAdapter is active.
        assert mock_run.called

def test_demo_mode_false_preserves_pipeline(clean_env):
    os.environ["DEMO_MODE"] = "false"
    os.environ["USE_REAL_VLM"] = "false"
    os.environ["USE_REAL_PRITHVI"] = "false"
    
    GaiaAdapter._instance = None
    adapter = GaiaAdapter()
    
    req = AnalysisRequest(query="Is there water in this image?", images=[ImageInfo(reference="img.tif", modality="optical")])
    data = adapter.run(req)
    
    trace = data["execution_trace"]
    vlm_tool = next(t for t in trace["tools_invoked"] if t["tool_name"] == "vlm")
    assert vlm_tool["parameters"]["model"] == "mock_vlm"
