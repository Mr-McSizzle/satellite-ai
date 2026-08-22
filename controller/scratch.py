with open("tests/test_gaia.py", "a") as f:
    f.write("""
def test_successful_execution_includes_confidence_and_audit(controller):
    req = make_request("Is there water in this image?", 1)
    res = controller.run(req)
    
    assert res["execution_trace"]["execution_status"] == "success"
    assert "confidence" in res
    assert "confidence_level" in res
    assert res["confidence"] > 0
    assert "audit" in res["execution_trace"]
    assert res["execution_trace"]["audit"]["audit_status"] == "passed"

def test_failed_execution_creates_recovery_decision(controller):
    req = make_request("What changed between these two images?", 2, fail_prithvi=True)
    res = controller.run(req)
    
    assert res["execution_trace"]["execution_status"] == "failed"
    assert "recovery" in res["execution_trace"]
    assert "recoverable" in res["execution_trace"]["recovery"]
    assert "audit" in res["execution_trace"]
""")
