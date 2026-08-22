import pytest
from controller.executor import Executor
from controller.registry import ToolRegistry

class SpyPrithvi:
    def __init__(self):
        self.call_count = 0
        self.last_task = None
        self.fail = False

    def process(self, task_id, request):
        self.call_count += 1
        self.last_task = task_id
        if self.fail:
            return {"status": "failed", "errors": ["Prithvi failed"], "evidence": []}
        return {"status": "success", "evidence": [{"type": "map", "data": "dummy"}], "errors": []}

class SpyVLM:
    def __init__(self):
        self.call_count = 0
        self.last_task = None
        self.last_context = None
        self.fail = False

    def run(self, task_id, request, context=None):
        self.call_count += 1
        self.last_task = task_id
        self.last_context = context
        if self.fail:
            return {"status": "failed", "errors": ["VLM failed"]}
        return {"status": "success", "answer": "VLM Answer", "evidence": []}

@pytest.fixture
def registry():
    return ToolRegistry()

@pytest.fixture
def executor(registry):
    return Executor(registry=registry, vlm=SpyVLM(), prithvi=SpyPrithvi())

def test_vqa_calls_vlm_once(executor):
    res = executor.execute("vqa", {})
    assert res["status"] == "success"
    assert executor.vlm.call_count == 1
    assert executor.prithvi.call_count == 0
    assert res["answer"] == "VLM Answer"

def test_captioning_calls_vlm_once(executor):
    res = executor.execute("captioning", {})
    assert res["status"] == "success"
    assert executor.vlm.call_count == 1

def test_grounding_calls_vlm_once(executor):
    res = executor.execute("grounding", {})
    assert res["status"] == "success"
    assert executor.vlm.call_count == 1

def test_change_vqa_flow(executor):
    res = executor.execute("change_vqa", {})
    assert res["status"] == "success"
    assert executor.prithvi.call_count == 1
    assert executor.vlm.call_count == 1
    # Check that VLM received Prithvi's context
    assert executor.vlm.last_context is not None
    assert "prithvi_evidence" in executor.vlm.last_context

def test_optical_sar_fusion_flow(executor):
    res = executor.execute("optical_sar_fusion", {})
    assert res["status"] == "success"
    assert executor.prithvi.call_count == 1
    assert executor.vlm.call_count == 1

def test_unsupported_task(executor):
    res = executor.execute("unknown", {})
    assert res["status"] == "failed"
    assert len(res["errors"]) > 0
    assert executor.prithvi.call_count == 0
    assert executor.vlm.call_count == 0

def test_prithvi_failure_prevents_vlm(executor):
    executor.prithvi.fail = True
    res = executor.execute("change_vqa", {})
    assert res["status"] == "failed"
    assert executor.prithvi.call_count == 1
    assert executor.vlm.call_count == 0
    assert "Prithvi failed" in res["errors"]

def test_vlm_failure_returned_cleanly(executor):
    executor.vlm.fail = True
    res = executor.execute("change_vqa", {})
    assert res["status"] == "failed"
    assert executor.prithvi.call_count == 1
    assert executor.vlm.call_count == 1
    assert "VLM failed" in res["errors"]
    # Prithvi evidence should still be present
    assert len(res["evidence"]) == 1

def test_successful_execution_structure(executor):
    res = executor.execute("change_vqa", {})
    assert res["task"] == "change_vqa"
    assert res["status"] == "success"
    assert res["answer"] == "VLM Answer"
    assert len(res["evidence"]) == 1
    assert len(res["tool_results"]) == 2
    assert res["tool_results"][0]["tool"] == "prithvi"
    assert res["tool_results"][1]["tool"] == "vlm"
