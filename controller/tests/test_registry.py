import pytest
from controller.registry import ToolRegistry, TaskDefinition

@pytest.fixture
def registry():
    return ToolRegistry()

def test_registry_construction(registry):
    # Verify that registry construction does not load any ML model or require CUDA
    # (By asserting it instantiates quickly and creates the expected pure-Python structures)
    assert isinstance(registry, ToolRegistry)
    assert hasattr(registry, "_registry")
    assert len(registry._registry) == 5

def test_supports_supported_tasks(registry):
    supported = ["vqa", "captioning", "grounding", "change_vqa", "optical_sar_fusion"]
    for task in supported:
        assert registry.supports(task) is True

def test_supports_unsupported_tasks(registry):
    unsupported = ["unknown", "", "random", "foo", "VQA ", None, 123]
    for task in unsupported:
        assert registry.supports(task) is False

def test_get_valid_mappings(registry):
    # vqa -> ["vlm"]
    defn = registry.get("vqa")
    assert defn.task_id == "vqa"
    assert defn.tools == ["vlm"]

    # captioning -> ["vlm"]
    defn = registry.get("captioning")
    assert defn.task_id == "captioning"
    assert defn.tools == ["vlm"]

    # grounding -> ["vlm"]
    defn = registry.get("grounding")
    assert defn.task_id == "grounding"
    assert defn.tools == ["vlm"]

    # change_vqa -> ["prithvi", "vlm"]
    defn = registry.get("change_vqa")
    assert defn.task_id == "change_vqa"
    assert defn.tools == ["prithvi", "vlm"]

    # optical_sar_fusion -> ["prithvi", "vlm"]
    defn = registry.get("optical_sar_fusion")
    assert defn.task_id == "optical_sar_fusion"
    assert defn.tools == ["prithvi", "vlm"]

def test_get_invalid_task_raises_exception(registry):
    with pytest.raises(ValueError, match="unknown or unsupported"):
        registry.get("unknown")
        
    with pytest.raises(ValueError):
        registry.get("")

    with pytest.raises(ValueError):
        registry.get(None)

    with pytest.raises(ValueError):
        registry.get("VQA ")
        
def test_task_definition_structure(registry):
    defn = registry.get("vqa")
    assert isinstance(defn, TaskDefinition)
    assert isinstance(defn.task_id, str)
    assert isinstance(defn.tools, list)
    assert isinstance(defn.description, str)
    assert len(defn.description) > 0
