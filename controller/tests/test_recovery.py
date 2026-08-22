import pytest
from controller.recovery import RecoveryEngine

def test_successful_execution():
    engine = RecoveryEngine()
    res = engine.analyze_failure({"execution_status": "success"})
    assert res["recoverable"] is False
    assert res["action"] == "none"

def test_prithvi_failure_vlm_success_fallback():
    engine = RecoveryEngine()
    res = engine.analyze_failure({
        "execution_status": "failed",
        "validation_result": {"valid": True},
        "tools_invoked": [
            {"tool_name": "prithvi", "execution_status": "failed"},
            {"tool_name": "vlm", "execution_status": "success"}
        ]
    })
    assert res["recoverable"] is True
    assert res["action"] == "fallback"

def test_validation_failure_abort():
    engine = RecoveryEngine()
    res = engine.analyze_failure({
        "execution_status": "failed",
        "validation_result": {"valid": False}
    })
    assert res["recoverable"] is False
    assert res["action"] == "abort"

def test_complete_failure_abort():
    engine = RecoveryEngine()
    res = engine.analyze_failure({
        "execution_status": "failed",
        "validation_result": {"valid": True},
        "tools_invoked": [
            {"tool_name": "prithvi", "execution_status": "failed"},
            {"tool_name": "vlm", "execution_status": "failed"}
        ]
    })
    assert res["recoverable"] is False
    assert res["action"] == "abort"
