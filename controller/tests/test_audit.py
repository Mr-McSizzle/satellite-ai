import pytest
from controller.audit import AuditEngine

def test_valid_result_passes_audit():
    engine = AuditEngine()
    res = engine.audit({}, {
        "task": "vqa",
        "execution_trace": {
            "execution_status": "success",
            "tools_invoked": [{"tool_name": "vlm"}]
        }
    })
    assert res["audit_status"] == "passed"
    
def test_missing_task_fails_audit():
    engine = AuditEngine()
    res = engine.audit({}, {
        "execution_trace": {
            "execution_status": "success",
            "tools_invoked": [{"tool_name": "vlm"}]
        }
    })
    assert res["audit_status"] == "failed"
    assert res["checks"]["task"] is False

def test_missing_tools_fails_audit():
    engine = AuditEngine()
    res = engine.audit({}, {
        "task": "vqa",
        "execution_trace": {
            "execution_status": "success",
            "tools_invoked": []
        }
    })
    assert res["audit_status"] == "failed"
    assert res["checks"]["tools"] is False

def test_missing_confidence_fails_only_when_expected():
    engine = AuditEngine()
    res = engine.audit({"require_confidence": False}, {
        "task": "vqa",
        "execution_trace": {
            "execution_status": "success",
            "tools_invoked": [{"tool_name": "vlm"}]
        }
    })
    assert res["audit_status"] == "passed"
    
    res2 = engine.audit({"require_confidence": True}, {
        "task": "vqa",
        "execution_trace": {
            "execution_status": "success",
            "tools_invoked": [{"tool_name": "vlm"}]
        }
    })
    assert res2["audit_status"] == "failed"
    assert res2["checks"]["confidence"] is False
