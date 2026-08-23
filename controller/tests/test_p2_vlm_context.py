import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from controller.models.p2_vlm_context import build_p2_vlm_context
from controller.models.vlm_adapter import RealVLMAdapter

def test_change_detection_context():
    p2_result = {
        "p2_task": "change_detection",
        "p2_confidence": 0.88,
        "p2_metrics": {
            "sensor_agreement_iou": 1.0,
            "cloud_penalty": 0.0,
            "terrain_penalty": 0.0
        }
    }
    ctx = build_p2_vlm_context(p2_result)
    assert "change mask" in ctx
    assert "Perception confidence: 0.88" in ctx
    assert "Sensor agreement IoU: 1.0" in ctx
    assert "Cloud penalty: 0.0" in ctx
    assert "Terrain penalty: 0.0" in ctx

def test_segmentation_context():
    p2_result = {
        "p2_task": "optical_segmentation",
        "p2_confidence": 0.95,
        "p2_metrics": {
            "cloud_penalty": -0.1
        }
    }
    ctx = build_p2_vlm_context(p2_result)
    assert "feature mask" in ctx
    assert "Perception confidence: 0.95" in ctx
    assert "Cloud penalty: -0.1" in ctx
    assert "Terrain penalty" not in ctx # Should not invent

def test_fusion_context():
    p2_result = {
        "p2_task": "optical_sar_fusion",
        "p2_confidence": 0.81,
        "p2_metrics": {
            "sensor_agreement_iou": 0.72,
            "cloud_penalty": 0.0,
            "terrain_penalty": -0.25
        }
    }
    ctx = build_p2_vlm_context(p2_result)
    assert "fusion mask" in ctx
    assert "Sensor agreement IoU: 0.72" in ctx
    assert "Terrain penalty: -0.25" in ctx

def test_missing_optional_metrics():
    p2_result = {
        "p2_task": "change_detection"
    }
    ctx = build_p2_vlm_context(p2_result)
    assert "change mask" in ctx
    assert "confidence" not in ctx

def test_malformed_p2_result():
    assert build_p2_vlm_context({}) == ""
    assert build_p2_vlm_context(None) == ""

@patch("controller.models.vlm_adapter.Path.exists", return_value=True)
@patch("controller.models.vlm_adapter.Path.is_dir", return_value=True)
def test_vlm_adapter_with_context(mock_isdir, mock_exists):
    # Setup mock P1_VLM_PATH and inference module
    os.environ["P1_VLM_PATH"] = "dummy"
    if "inference" not in sys.modules:
        sys.modules["inference"] = MagicMock()
    
    mock_vlm_answer = MagicMock()
    mock_vlm_answer.return_value = {"answer": "Some answer", "metadata": {}}
    sys.modules["inference"].vlm_answer = mock_vlm_answer
    
    adapter = RealVLMAdapter()

    req = {"images": [{"reference": "test.tif"}], "question": "What is this?"}
    context = {
        "prithvi_evidence": [
            {
                "type": "prithvi_mask",
                "data": {
                    "uri": "mask.tif",
                    "p2_task": "change_detection",
                    "p2_confidence": 0.9,
                    "p2_metrics": {}
                }
            }
        ]
    }
    
    res = adapter.run("change_vqa", req, context)
    
    assert res["status"] == "success"
    assert res["metadata"]["p2_context_used"] is True
    assert res["metadata"]["p2_context_source"] == "prithvi_p2"
    assert res["metadata"]["p2_mask_path"] == "mask.tif"
    
    # Check vlm_answer called with right args
    mock_vlm_answer.assert_called_once()
    kwargs = mock_vlm_answer.call_args[1]
    assert "EXTERNAL PERCEPTION CONTEXT" in kwargs["question"]
    assert "What is this?" in kwargs["question"]
    assert kwargs["evidence"] is None

@patch("controller.models.vlm_adapter.Path.exists", return_value=True)
@patch("controller.models.vlm_adapter.Path.is_dir", return_value=True)
def test_no_p2_context(mock_isdir, mock_exists):
    os.environ["P1_VLM_PATH"] = "dummy"
    if "inference" not in sys.modules:
        sys.modules["inference"] = MagicMock()
        
    mock_vlm_answer = MagicMock()
    mock_vlm_answer.return_value = {"answer": "Some answer", "metadata": {}}
    sys.modules["inference"].vlm_answer = mock_vlm_answer
    
    adapter = RealVLMAdapter()
    req = {"images": [{"reference": "test.tif"}], "question": "Original Q"}
    
    res = adapter.run("vqa", req, {})
    
    mock_vlm_answer.assert_called_once()
    kwargs = mock_vlm_answer.call_args[1]
    assert kwargs["question"] == "Original Q"
    assert kwargs["evidence"] is None
