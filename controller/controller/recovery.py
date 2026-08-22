class RecoveryEngine:
    def analyze_failure(self, execution_result: dict) -> dict:
        status = execution_result.get("execution_status", "unknown")
        
        if status == "success":
            return {
                "recoverable": False,
                "action": "none",
                "reason": "Execution completed successfully"
            }
            
        validation_valid = execution_result.get("validation_result", {}).get("valid", True)
        if not validation_valid:
            return {
                "recoverable": False,
                "action": "abort",
                "reason": "Invalid input cannot be recovered"
            }
            
        tools_invoked = execution_result.get("tools_invoked", [])
        
        prithvi_failed = any(t.get("tool_name") == "prithvi" and t.get("execution_status") != "success" for t in tools_invoked)
        vlm_succeeded = any(t.get("tool_name") == "vlm" and t.get("execution_status") == "success" for t in tools_invoked)
        all_failed = all(t.get("execution_status") != "success" for t in tools_invoked) and len(tools_invoked) > 0
        
        if vlm_succeeded and prithvi_failed:
            return {
                "recoverable": True,
                "action": "fallback",
                "reason": "Use VLM-only response without perception evidence"
            }
            
        if all_failed:
            return {
                "recoverable": False,
                "action": "abort",
                "reason": "All tools failed"
            }
            
        return {
            "recoverable": False,
            "action": "abort",
            "reason": "Unrecoverable execution failure"
        }
