class ConfidenceEngine:
    def calculate(self, signals: dict) -> dict:
        tool_confidences = signals.get("tool_confidences", [])
        if tool_confidences:
            base_score = sum(tool_confidences) / len(tool_confidences)
        else:
            base_score = 0.5
            
        validation_valid = signals.get("validation_valid", True)
        if not validation_valid:
            base_score -= 0.3
            
        evidence_available = signals.get("evidence_available", True)
        if not evidence_available:
            base_score -= 0.2
            
        final_score = max(0.0, min(1.0, base_score))
        
        if final_score >= 0.8:
            level = "high"
        elif final_score >= 0.5:
            level = "medium"
        else:
            level = "low"
            
        return {
            "confidence": float(final_score),
            "level": level
        }
