import pytest
from controller.trace import TraceRecorder

def test_minimal_trace():
    recorder = TraceRecorder()
    recorder.set_task("vqa")
    recorder.set_status("success")
    trace = recorder.build()
    
    assert trace["task_selected"] == "vqa"
    assert trace["execution_status"] == "success"
    assert trace["tools_invoked"] == []
    assert trace["validation_result"] == {}

def test_build_without_task_raises_error():
    recorder = TraceRecorder()
    with pytest.raises(ValueError, match="task_selected must be set"):
        recorder.build()

def test_successful_execution_trace():
    recorder = TraceRecorder()
    recorder.set_task("change_vqa")
    recorder.set_validation({"valid": True, "info": "ok"})
    
    recorder.record_tool(
        tool_name="prithvi",
        status="success",
        parameters={"model_variant": "eo-2.0"},
        warnings=["Some minor issue"]
    )
    
    recorder.record_tool(
        tool_name="vlm",
        status="success",
        parameters={"temperature": 0.7}
    )
    
    recorder.set_status("success")
    
    trace = recorder.build()
    
    assert trace["task_selected"] == "change_vqa"
    assert trace["validation_result"] == {"valid": True, "info": "ok"}
    assert len(trace["tools_invoked"]) == 2
    
    assert trace["tools_invoked"][0]["tool_name"] == "prithvi"
    assert trace["tools_invoked"][0]["execution_status"] == "success"
    assert trace["tools_invoked"][0]["warnings"] == ["Some minor issue"]
    assert trace["tools_invoked"][0]["parameters"]["model_variant"] == "eo-2.0"
    
    assert trace["tools_invoked"][1]["tool_name"] == "vlm"
    assert trace["tools_invoked"][1]["execution_status"] == "success"
    assert trace["tools_invoked"][1]["parameters"]["temperature"] == 0.7

def test_failed_tool_execution():
    recorder = TraceRecorder()
    recorder.set_task("optical_sar_fusion")
    
    recorder.record_tool(
        tool_name="prithvi",
        status="failed",
        errors=["CUDA OOM"]
    )
    
    recorder.set_status("failed")
    recorder.add_error("Pipeline halted due to Prithvi failure")
    
    trace = recorder.build()
    assert trace["execution_status"] == "failed"
    assert trace["errors"] == ["Pipeline halted due to Prithvi failure"]
    assert len(trace["tools_invoked"]) == 1
    assert trace["tools_invoked"][0]["execution_status"] == "failed"
    assert trace["tools_invoked"][0]["errors"] == ["CUDA OOM"]

def test_warnings_and_errors():
    recorder = TraceRecorder()
    recorder.set_task("vqa")
    recorder.set_status("success")
    recorder.add_warning("Global warning 1")
    recorder.add_warning("Global warning 2")
    recorder.add_error("Non-fatal global error")
    
    trace = recorder.build()
    assert len(trace["warnings"]) == 2
    assert len(trace["errors"]) == 1
    assert "Global warning 1" in trace["warnings"]
    assert "Non-fatal global error" in trace["errors"]
