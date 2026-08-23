import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import builtins

from controller.models.vlm_adapter import RealVLMAdapter
from backend.app.services.gaia_adapter import GaiaAdapter

@pytest.fixture
def clean_env():
    # Store original
    orig = os.environ.copy()
    yield
    # Restore original
    os.environ.clear()
    os.environ.update(orig)
    if "inference" in sys.modules:
        del sys.modules["inference"]

def test_missing_p1_path(clean_env):
    if "P1_VLM_PATH" in os.environ:
        del os.environ["P1_VLM_PATH"]
    adapter = RealVLMAdapter()
    res = adapter.run("vqa", {"images": []})
    assert res["status"] == "failed"
    assert "P1_VLM_PATH environment variable is missing" in res["errors"][0]

def test_missing_image(clean_env, tmp_path):
    os.environ["P1_VLM_PATH"] = str(tmp_path)
    sys.modules["inference"] = MagicMock()
    adapter = RealVLMAdapter()
    res = adapter.run("vqa", {"images": [{"reference": str(tmp_path / "nonexistent.tif")}]})
    assert res["status"] == "failed"
    assert "Image path missing" in res["errors"][0]

def test_optical_sar_fusion_mapped_to_vqa(clean_env, tmp_path):
    os.environ["P1_VLM_PATH"] = str(tmp_path)
    
    mock_inference = MagicMock()
    mock_inference.vlm_answer.return_value = {"answer": "fusion", "metadata": {}}
    sys.modules["inference"] = mock_inference
    
    # Needs valid image so it reaches the P1 call
    open(str(tmp_path / "img.tif"), "w").close()
    
    adapter = RealVLMAdapter()
    res = adapter.run("optical_sar_fusion", {"images": [{"reference": str(tmp_path / "img.tif")}]})
    
    mock_inference.vlm_answer.assert_called_once()
    assert mock_inference.vlm_answer.call_args[1]["task"] == "vqa"

@patch("controller.models.vlm_adapter.Path.exists", return_value=True)
def test_task_mapping_and_success_result(mock_exists, clean_env, tmp_path):
    os.environ["P1_VLM_PATH"] = str(tmp_path)
    
    mock_inference = MagicMock()
    mock_vlm_answer = MagicMock()
    mock_vlm_answer.return_value = {
        "answer": "A test answer",
        "task": "caption",
        "regions": [{"x": 10, "y": 20}],
        "confidence": 0.95,
        "model": "p1-7b",
        "checkpoint": "470349a",
        "metadata": {"status": "success", "extra": "info"}
    }
    mock_inference.vlm_answer = mock_vlm_answer
    sys.modules["inference"] = mock_inference
    
    adapter = RealVLMAdapter()
    
    # Test captioning -> caption
    request = {
        "question": "Describe this",
        "images": [{"reference": "test1.tif"}, {"reference": "test2.tif"}]
    }
    
    res = adapter.run("captioning", request)
    
    assert res["status"] == "success"
    assert res["answer"] == "A test answer"
    assert res["evidence"] == [{"x": 10, "y": 20}]
    assert res["metadata"]["model"] == "p1-7b"
    assert res["metadata"]["confidence"] == 0.95
    assert res["metadata"]["extra"] == "info"
    
    # Verify mock called correctly
    mock_vlm_answer.assert_called_once_with(
        images=["test1.tif", "test2.tif"], # Order preserved
        question="Describe this",
        evidence=None,
        task="caption"
    )

@patch("controller.models.vlm_adapter.Path.exists", return_value=True)
def test_error_result_mapping(mock_exists, clean_env, tmp_path):
    os.environ["P1_VLM_PATH"] = str(tmp_path)
    
    mock_inference = MagicMock()
    mock_vlm_answer = MagicMock()
    mock_vlm_answer.return_value = {
        "answer": None,
        "metadata": {"status": "error", "error": "P1 internal failure"}
    }
    mock_inference.vlm_answer = mock_vlm_answer
    sys.modules["inference"] = mock_inference
    
    adapter = RealVLMAdapter()
    res = adapter.run("vqa", {"images": [{"reference": "img.tif"}]})
    
    assert res["status"] == "failed"
    assert "P1 internal failure" in res["errors"]
    mock_vlm_answer.assert_called_once_with(
        images=["img.tif"],
        question="",
        evidence=None,
        task="vqa"
    )

@patch("controller.models.vlm_adapter.Path.exists", return_value=True)
def test_other_tasks(mock_exists, clean_env, tmp_path):
    os.environ["P1_VLM_PATH"] = str(tmp_path)
    
    mock_inference = MagicMock()
    mock_vlm_answer = MagicMock()
    mock_vlm_answer.return_value = {"metadata": {}}
    mock_inference.vlm_answer = mock_vlm_answer
    sys.modules["inference"] = mock_inference
    
    adapter = RealVLMAdapter()
    
    adapter.run("grounding", {})
    assert mock_vlm_answer.call_args[1]["task"] == "grounding"
    
    adapter.run("change_vqa", {})
    assert mock_vlm_answer.call_args[1]["task"] == "change_vqa"

def test_use_real_vlm_false_does_not_import_p1(clean_env):
    os.environ["USE_REAL_VLM"] = "false"
    
    # Reset singleton if already initialized
    GaiaAdapter._instance = None
    
    original_import = builtins.__import__
    def side_effect(name, *args, **kwargs):
        if name == "inference":
            raise AssertionError("Should not have imported 'inference'!")
        return original_import(name, *args, **kwargs)
        
    with patch("builtins.__import__", side_effect=side_effect):
        adapter = GaiaAdapter()
        
    from mocks.mock_vlm import MockVLM
    assert isinstance(adapter._controller.executor.vlm, MockVLM)

def test_use_real_vlm_true_uses_realvlm(clean_env):
    os.environ["USE_REAL_VLM"] = "true"
    
    # Reset singleton if already initialized
    GaiaAdapter._instance = None
    
    adapter = GaiaAdapter()
    assert isinstance(adapter._controller.executor.vlm, RealVLMAdapter)
