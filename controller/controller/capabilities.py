class CapabilityRegistry:
    def __init__(self):
        self.catalogue = {
            "prithvi": {
                "capabilities": [
                    "segmentation",
                    "change_detection",
                    "fusion_analysis"
                ],
                "requires": [
                    "satellite_image"
                ],
                "produces": [
                    "mask",
                    "change_map",
                    "statistics"
                ]
            },
            "vlm": {
                "capabilities": [
                    "question_answering",
                    "captioning",
                    "grounding",
                    "explanation"
                ],
                "requires": [
                    "image",
                    "question"
                ],
                "produces": [
                    "text_answer"
                ]
            }
        }
        
    def get_capabilities(self, tool_name: str) -> dict:
        if not tool_name or tool_name not in self.catalogue:
            raise ValueError(f"Unknown tool: {tool_name}")
        return self.catalogue[tool_name]
        
    def find_tools(self, capability: str) -> list:
        if not capability or not isinstance(capability, str):
            raise ValueError("Capability cannot be empty")
            
        matching_tools = []
        for tool, info in self.catalogue.items():
            if capability in info["capabilities"]:
                matching_tools.append(tool)
                
        if not matching_tools:
            raise ValueError(f"No tools found for capability: {capability}")
            
        return matching_tools
