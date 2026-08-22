import pytest
from controller.capabilities import CapabilityRegistry

def test_prithvi_capabilities():
    registry = CapabilityRegistry()
    caps = registry.get_capabilities("prithvi")
    assert "change_detection" in caps["capabilities"]
    assert "satellite_image" in caps["requires"]
    assert "change_map" in caps["produces"]

def test_vlm_capabilities():
    registry = CapabilityRegistry()
    caps = registry.get_capabilities("vlm")
    assert "question_answering" in caps["capabilities"]
    assert "image" in caps["requires"]
    assert "text_answer" in caps["produces"]

def test_find_tools_change_detection():
    registry = CapabilityRegistry()
    tools = registry.find_tools("change_detection")
    assert "prithvi" in tools

def test_find_tools_explanation():
    registry = CapabilityRegistry()
    tools = registry.find_tools("explanation")
    assert "vlm" in tools

def test_invalid_tool_raises_error():
    registry = CapabilityRegistry()
    with pytest.raises(ValueError):
        registry.get_capabilities("unknown_tool")

def test_invalid_capability_raises_error():
    registry = CapabilityRegistry()
    with pytest.raises(ValueError):
        registry.find_tools("unknown_capability")
