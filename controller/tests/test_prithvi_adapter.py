import os
import sys
import pytest
import builtins
from unittest.mock import patch, MagicMock

from controller.models.prithvi_adapter import RealPrithviAdapter
from backend.app.services.gaia_adapter import GaiaAdapter

@pytest.fixture
def clean_env():
    orig = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(orig)

class MockPerceptionResult:
    def __init__(self, task, status, evidence_mask_path, confidence, metrics, execution_trace):
        self.task = task
        self.status = status
        self.evidence_mask_path = evidence_mask_path
        self.confidence = confidence
        self.metrics = metrics
        self.execution_trace = execution_trace

class MockValidationMetrics:
    def __init__(self, iou, cp, tp):
        self.sensor_agreement_iou = iou
        self.cloud_penalty = cp
        self.terrain_penalty = tp

def test_change_vqa(clean_env):
    mock_fusion = MagicMock()
    mock_fusion.process_change_detection.return_value = MockPerceptionResult(
        task="change_detection", status="success", evidence_mask_path="out.tif",
        confidence=0.88, metrics=MockValidationMetrics(1.0, 0.0, 0.0),
        execution_trace=["trace"]
    )
    sys.modules["fusion_engine"] = mock_fusion
    adapter = RealPrithviAdapter()
    
    req = {"images": [{"reference": "img1.tif", "modality": "optical"}, {"reference": "img2.tif", "modality": "optical"}]}
    res = adapter.process("change_vqa", req)
    
    assert res["status"] == "success"
    assert res["evidence"][0]["data"]["uri"] == "out.tif"
    assert res["metadata"]["p2_confidence"] == 0.88
    assert res["metadata"]["p2_metrics"]["sensor_agreement_iou"] == 1.0

def test_optical_segmentation(clean_env):
    mock_fusion = MagicMock()
    mock_fusion.process_single_optical_segmentation.return_value = MockPerceptionResult(
        task="optical_segmentation", status="success", evidence_mask_path="seg.tif",
        confidence=0.9, metrics=MockValidationMetrics(1.0, 0.0, 0.0),
        execution_trace=["trace"]
    )
    sys.modules["fusion_engine"] = mock_fusion
    adapter = RealPrithviAdapter()
    
    req = {"images": [{"reference": "opt.tif", "modality": "optical"}]}
    res = adapter.process("optical_segmentation", req)
    assert res["status"] == "success"
    assert res["evidence"][0]["data"]["uri"] == "seg.tif"

def test_optical_sar_fusion(clean_env):
    mock_fusion = MagicMock()
    mock_fusion.process_optical_sar_fusion.return_value = MockPerceptionResult(
        task="optical_sar_fusion", status="success", evidence_mask_path="fus.tif",
        confidence=0.7, metrics=MockValidationMetrics(0.8, -0.1, 0.0),
        execution_trace=["fustrace"]
    )
    sys.modules["fusion_engine"] = mock_fusion
    adapter = RealPrithviAdapter()
    
    req = {"images": [{"reference": "opt.tif", "modality": "optical"}, {"reference": "sar.tif", "modality": "sar"}]}
    res = adapter.process("optical_sar_fusion", req)
    assert res["status"] == "success"
    assert res["evidence"][0]["data"]["uri"] == "fus.tif"
    assert res["metadata"]["p2_execution_trace"] == ["fustrace"]

def test_missing_image_change_vqa():
    adapter = RealPrithviAdapter()
    req = {"images": [{"reference": "img1.tif"}]}
    res = adapter.process("change_vqa", req)
    assert res["status"] == "failed"
    assert "least two images" in res["errors"][0]

def test_missing_modality_optical_sar_fusion():
    adapter = RealPrithviAdapter()
    req = {"images": [{"reference": "opt.tif", "modality": "optical"}]}
    res = adapter.process("optical_sar_fusion", req)
    assert res["status"] == "failed"
    assert "Missing required optical or sar modality" in res["errors"][0]

def test_p2_failure_result(clean_env):
    mock_fusion = MagicMock()
    mock_fusion.process_single_optical_segmentation.return_value = MockPerceptionResult(
        task="optical_segmentation", status="error", evidence_mask_path=None,
        confidence=0.1, metrics=MockValidationMetrics(0,0,0),
        execution_trace=["fail"]
    )
    sys.modules["fusion_engine"] = mock_fusion
    adapter = RealPrithviAdapter()
    req = {"images": [{"reference": "opt.tif", "modality": "optical"}]}
    res = adapter.process("optical_segmentation", req)
    assert res["status"] == "failed"

def test_unsupported_task():
    adapter = RealPrithviAdapter()
    res = adapter.process("vqa", {"images": []})
    assert res["status"] == "success"
    assert "not supported by P2; bypassing" in res["warnings"][0]

def test_use_real_prithvi_false_keeps_mock(clean_env):
    os.environ["USE_REAL_PRITHVI"] = "false"
    GaiaAdapter._instance = None
    
    adapter = GaiaAdapter()
    from mocks.mock_prithvi import MockPrithvi
    assert isinstance(adapter._controller.executor.prithvi, MockPrithvi)
