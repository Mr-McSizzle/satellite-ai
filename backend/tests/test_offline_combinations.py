import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Mock boundaries before importing app
sys.modules["inference"] = MagicMock()
sys.modules["fusion_engine"] = MagicMock()

from backend.app.main import app
from backend.app.services.gaia_adapter import GaiaAdapter
from backend.app.schemas.analysis import AnalysisRequest, ImageInfo

@pytest.fixture
def clean_env():
    orig_vlm = os.environ.get("USE_REAL_VLM")
    orig_prithvi = os.environ.get("USE_REAL_PRITHVI")
    orig_p1_path = os.environ.get("P1_VLM_PATH")
    
    os.environ["P1_VLM_PATH"] = "dummy"
    
    GaiaAdapter._instance = None # Reset singleton
    
    yield
    
    GaiaAdapter._instance = None
    if orig_vlm is not None:
        os.environ["USE_REAL_VLM"] = orig_vlm
    elif "USE_REAL_VLM" in os.environ:
        del os.environ["USE_REAL_VLM"]
        
    if orig_prithvi is not None:
        os.environ["USE_REAL_PRITHVI"] = orig_prithvi
    elif "USE_REAL_PRITHVI" in os.environ:
        del os.environ["USE_REAL_PRITHVI"]
        
    if orig_p1_path is not None:
        os.environ["P1_VLM_PATH"] = orig_p1_path
    elif "P1_VLM_PATH" in os.environ:
        del os.environ["P1_VLM_PATH"]

def create_mock_p2_result(task, status="success"):
    # Since we dynamically import this in RealPrithviAdapter, we must ensure the mock returns an object
    class MockValidationMetrics:
        def __init__(self, iou, cp, tp):
            self.sensor_agreement_iou = iou
            self.cloud_penalty = cp
            self.terrain_penalty = tp

    class MockPerceptionResult:
        def __init__(self, t, s, emp, c, m, et):
            self.task = t
            self.status = s
            self.evidence_mask_path = emp
            self.confidence = c
            self.metrics = m
            self.execution_trace = et
            
    return MockPerceptionResult(
        task, status, "mask.tif", 0.99, 
        MockValidationMetrics(1.0, 0.0, 0.0), ["p2_trace"]
    )

@patch("controller.models.vlm_adapter.Path.is_dir", return_value=True)
@patch("controller.models.vlm_adapter.Path.exists", return_value=True)
def test_combination_mock_mock(mock_exists, mock_isdir, clean_env):
    os.environ["USE_REAL_VLM"] = "false"
    os.environ["USE_REAL_PRITHVI"] = "false"
    
    adapter = GaiaAdapter()
    req = AnalysisRequest(query="Detect changes", images=[ImageInfo(reference="a.tif", modality="optical"), ImageInfo(reference="b.tif", modality="optical")])
    data = adapter.run(req)
    assert data["execution_trace"]["execution_status"] == "success"
    
    trace = data["execution_trace"]
    prithvi_tool = next(t for t in trace["tools_invoked"] if t["tool_name"] == "prithvi")
    vlm_tool = next(t for t in trace["tools_invoked"] if t["tool_name"] == "vlm")
    
    assert vlm_tool["parameters"]["model"] == "mock_vlm"
    assert "Mock" in str(prithvi_tool)

@patch("controller.models.vlm_adapter.Path.is_dir", return_value=True)
@patch("controller.models.vlm_adapter.Path.exists", return_value=True)
def test_combination_real_prithvi_mock_vlm(mock_exists, mock_isdir, clean_env):
    os.environ["USE_REAL_VLM"] = "false"
    os.environ["USE_REAL_PRITHVI"] = "true"
    
    sys.modules["fusion_engine"].process_change_detection.return_value = create_mock_p2_result("change_detection")
    
    adapter = GaiaAdapter()
    req = AnalysisRequest(query="Detect changes", images=[ImageInfo(reference="a.tif", modality="optical"), ImageInfo(reference="b.tif", modality="optical")])
    data = adapter.run(req)
    assert data["execution_trace"]["execution_status"] == "success"
    
    trace = data["execution_trace"]
    vlm_tool = next(t for t in trace["tools_invoked"] if t["tool_name"] == "vlm")
    
    assert vlm_tool["parameters"]["model"] == "mock_vlm"
    sys.modules["fusion_engine"].process_change_detection.assert_called()

@patch("controller.models.vlm_adapter.Path.is_dir", return_value=True)
@patch("controller.models.vlm_adapter.Path.exists", return_value=True)
def test_combination_mock_prithvi_real_vlm(mock_exists, mock_isdir, clean_env):
    os.environ["USE_REAL_VLM"] = "true"
    os.environ["USE_REAL_PRITHVI"] = "false"
    
    sys.modules["inference"].vlm_answer.return_value = {"answer": "P1 answer", "model": "satquery-vlm", "metadata": {}}
    
    adapter = GaiaAdapter()
    req = AnalysisRequest(query="Detect changes", images=[ImageInfo(reference="a.tif", modality="optical"), ImageInfo(reference="b.tif", modality="optical")])
    data = adapter.run(req)
    assert data["execution_trace"]["execution_status"] == "success"
    
    trace = data["execution_trace"]
    vlm_tool = next(t for t in trace["tools_invoked"] if t["tool_name"] == "vlm")
    
    assert vlm_tool["parameters"]["model"] == "satquery-vlm"
    args, kwargs = sys.modules["inference"].vlm_answer.call_args
    assert "EXTERNAL PERCEPTION CONTEXT" not in kwargs["question"]

@patch("controller.models.vlm_adapter.Path.is_dir", return_value=True)
@patch("controller.models.vlm_adapter.Path.exists", return_value=True)
def test_combination_real_real(mock_exists, mock_isdir, clean_env):
    os.environ["USE_REAL_VLM"] = "true"
    os.environ["USE_REAL_PRITHVI"] = "true"
    
    sys.modules["fusion_engine"].process_change_detection.return_value = create_mock_p2_result("change_detection")
    sys.modules["inference"].vlm_answer.return_value = {"answer": "P1 answer", "model": "satquery-vlm", "metadata": {}}
    
    adapter = GaiaAdapter()
    req = AnalysisRequest(query="Detect changes", images=[ImageInfo(reference="a.tif", modality="optical"), ImageInfo(reference="b.tif", modality="optical")])
    data = adapter.run(req)
    assert data["execution_trace"]["execution_status"] == "success"
    
    trace = data["execution_trace"]
    vlm_tool = next(t for t in trace["tools_invoked"] if t["tool_name"] == "vlm")
    
    assert vlm_tool["parameters"]["model"] == "satquery-vlm"
    assert vlm_tool["parameters"]["p2_context_used"] is True
    assert vlm_tool["parameters"]["p2_context_source"] == "prithvi_p2"
    
    args, kwargs = sys.modules["inference"].vlm_answer.call_args
    assert "EXTERNAL PERCEPTION CONTEXT" in kwargs["question"]
    assert "Perception confidence: 0.99" in kwargs["question"]
    assert "Sensor agreement IoU: 1.0" in kwargs["question"]
    assert "Detect changes" in kwargs["question"]
    assert kwargs["evidence"] is None
    
    assert "changed_fraction" not in kwargs["question"]
    assert "dominant_region" not in kwargs["question"]

@patch("controller.models.vlm_adapter.Path.is_dir", return_value=True)
@patch("controller.models.vlm_adapter.Path.exists", return_value=True)
def test_failure_propagation(mock_exists, mock_isdir, clean_env):
    os.environ["USE_REAL_VLM"] = "true"
    os.environ["USE_REAL_PRITHVI"] = "true"
    
    sys.modules["fusion_engine"].process_change_detection.return_value = create_mock_p2_result("change_detection", "error")
    sys.modules["inference"].vlm_answer.return_value = {"answer": "P1 recovered", "model": "satquery-vlm", "metadata": {}}
    
    adapter = GaiaAdapter()
    req = AnalysisRequest(query="Detect changes", images=[ImageInfo(reference="a.tif", modality="optical"), ImageInfo(reference="b.tif", modality="optical")])
    data = adapter.run(req)
    
    assert data["execution_trace"]["execution_status"] == "failed"
    
    trace = data["execution_trace"]
    prithvi_tool = next(t for t in trace["tools_invoked"] if t["tool_name"] == "prithvi")
    assert prithvi_tool["execution_status"] == "failed"
    
    vlm_tool_list = [t for t in trace["tools_invoked"] if t["tool_name"] == "vlm"]
    assert len(vlm_tool_list) == 0

@patch("controller.models.vlm_adapter.Path.is_dir", return_value=True)
@patch("controller.models.vlm_adapter.Path.exists", return_value=True)
def test_p1_failure_propagation(mock_exists, mock_isdir, clean_env):
    os.environ["USE_REAL_VLM"] = "true"
    os.environ["USE_REAL_PRITHVI"] = "true"
    
    sys.modules["fusion_engine"].process_change_detection.return_value = create_mock_p2_result("change_detection")
    sys.modules["inference"].vlm_answer.side_effect = Exception("CUDA OOM")
    
    adapter = GaiaAdapter()
    req = AnalysisRequest(query="Detect changes", images=[ImageInfo(reference="a.tif", modality="optical"), ImageInfo(reference="b.tif", modality="optical")])
    data = adapter.run(req)
    
    assert data["execution_trace"]["execution_status"] == "failed"
    assert "CUDA OOM" in str(data["execution_trace"]["errors"])
