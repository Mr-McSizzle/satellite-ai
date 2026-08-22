class MockPrithvi:
    def process(self, task_id: str, request: dict) -> dict:
        """
        Mocks the Prithvi execution.
        """
        # If there's an injected failure flag in the request, fail it for testing
        if request.get("fail_prithvi"):
            return {
                "status": "failed",
                "errors": ["Simulated Prithvi failure"],
                "warnings": []
            }
            
        return {
            "status": "success",
            "results": [{"info": f"Mock Prithvi perception for {task_id}"}],
            "evidence": [{"type": "mock_map", "data": {"uri": "mock.tif"}}],
            "metrics": {},
            "errors": [],
            "warnings": []
        }
