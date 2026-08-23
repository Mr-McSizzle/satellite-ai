import pytest
import os
from unittest.mock import patch, MagicMock
from controller.models.gemini_demo_adapter import GeminiDemoAdapter

@pytest.fixture
def clean_env():
    orig_demo = os.environ.get("DEMO_MODE")
    orig_scenario = os.environ.get("DEMO_SCENARIO")
    yield
    if orig_demo is not None:
        os.environ["DEMO_MODE"] = orig_demo
    elif "DEMO_MODE" in os.environ:
        del os.environ["DEMO_MODE"]
        
    if orig_scenario is not None:
        os.environ["DEMO_SCENARIO"] = orig_scenario
    elif "DEMO_SCENARIO" in os.environ:
        del os.environ["DEMO_SCENARIO"]

def test_adapter_no_client():
    # When initialized without google.genai or key, it fails gracefully
    with patch.dict('sys.modules', {'google.genai': None}):
        adapter = GeminiDemoAdapter()
        res = adapter.run("vqa", {"query": "Hello"}, {})
        assert res["status"] == "failed"
        assert "Gemini SDK not installed" in res["errors"][0]
        assert res["metadata"]["demo_mode"] is True

@patch("controller.models.gemini_demo_adapter.Image.open")
def test_change_vqa_images(mock_open, clean_env):
    adapter = GeminiDemoAdapter()
    adapter.has_client = True
    adapter.client = MagicMock()
    
    mock_open.return_value.convert.return_value = "fake_image_obj"
    
    mock_response = MagicMock()
    mock_response.text = '{"answer": "Changes", "confidence": 0.8, "evidence_type": ["observed"]}'
    adapter.client.models.generate_content.return_value = mock_response
    
    req = {
        "query": "Detect changes",
        "images": [{"reference": "before.tif"}, {"reference": "after.tif"}]
    }
    
    res = adapter.run("change_vqa", req)
    
    assert res["status"] == "success"
    assert res["answer"] == "Changes"
    assert res["metadata"]["demo_mode"] is True
    assert res["metadata"]["provenance"] == "demo_inference"
    
    # Check contents passed
    contents = adapter.client.models.generate_content.call_args[1]["contents"]
    assert "IMAGE 1 (BEFORE)" in contents
    assert "IMAGE 2 (AFTER)" in contents

@patch("controller.models.gemini_demo_adapter.Image.open")
def test_optical_sar_selection(mock_open, clean_env):
    adapter = GeminiDemoAdapter()
    adapter.has_client = True
    adapter.client = MagicMock()
    
    mock_open.return_value.convert.return_value = "fake_image_obj"
    
    mock_response = MagicMock()
    mock_response.text = '{"answer": "Fusion done"}'
    adapter.client.models.generate_content.return_value = mock_response
    
    req = {
        "query": "Do fusion",
        "images": [
            {"reference": "opt.tif", "modality": "optical"},
            {"reference": "sar.tif", "modality": "SAR"}
        ]
    }
    
    res = adapter.run("optical_sar_fusion", req)
    
    contents = adapter.client.models.generate_content.call_args[1]["contents"]
    assert any("IMAGE 1 (optical)" in c for c in contents if isinstance(c, str))
    assert any("IMAGE 2 (SAR)" in c for c in contents if isinstance(c, str))

def test_grounding_trigger(clean_env):
    adapter = GeminiDemoAdapter()
    adapter.has_client = True
    adapter.client = MagicMock()
    
    mock_response = MagicMock()
    mock_response.text = '{"answer": "Growth!"}'
    # Simulate grounding metadata returned
    class MockCand:
        class MockMetadata:
            web_search_queries = ["business growth in area"]
            grounding_chunks = []
        grounding_metadata = MockMetadata()
    
    mock_response.candidates = [MockCand()]
    adapter.client.models.generate_content.return_value = mock_response
    
    req = {"query": "Is there business growth?"}
    res = adapter.run("vqa", req)
    
    # Needs grounding because "business" is in query
    config = adapter.client.models.generate_content.call_args[1]["config"]
    assert config.tools is not None
    assert len(config.tools) == 1
    
    assert res["metadata"]["web_grounding_used"] is True

def test_gemini_failure_structured():
    adapter = GeminiDemoAdapter()
    adapter.has_client = True
    adapter.client = MagicMock()
    adapter.client.models.generate_content.side_effect = Exception("API error")
    
    res = adapter.run("vqa", {"query": "fail"}, {})
    assert res["status"] == "failed"
    assert "Gemini demo failure: API error" in res["errors"][0]
