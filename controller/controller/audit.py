class AuditEngine:
    def audit(self, request: dict, result: dict) -> dict:
        checks = {
            "task": "task" in result and bool(result["task"]),
            "execution": "execution_trace" in result and "execution_status" in result["execution_trace"] and bool(result["execution_trace"]["execution_status"]),
            "tools": "execution_trace" in result and "tools_invoked" in result["execution_trace"] and len(result["execution_trace"]["tools_invoked"]) > 0,
            "confidence": True
        }
        
        expect_confidence = request.get("require_confidence", False)
        if expect_confidence and "confidence" not in result:
            checks["confidence"] = False
            
        audit_status = "passed" if all(checks.values()) else "failed"
        
        return {
            "audit_status": audit_status,
            "checks": checks
        }
