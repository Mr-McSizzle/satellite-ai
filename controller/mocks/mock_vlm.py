class MockVLM:
    def run(self, task_id: str, request: dict, context: dict = None) -> dict:
        """
        Mocks the VLM execution.
        """
        # If there's an injected failure flag in the request, fail it for testing
        if request.get("fail_vlm"):
            return {
                "status": "failed",
                "errors": ["Simulated VLM failure"],
                "warnings": []
            }
            
        return {
            "status": "success",
            "answer": f"Mock VLM answer for {task_id}",
            "evidence": [],
            "metadata": {"model": "mock_vlm"},
            "errors": [],
            "warnings": []
        }
