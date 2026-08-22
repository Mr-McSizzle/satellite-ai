import re
from dataclasses import dataclass, field
from typing import List

@dataclass
class ClassificationResult:
    """Represents the structured output of the task classifier."""
    task: str
    confidence: float
    matched_signals: List[str] = field(default_factory=list)

class QuestionClassifier:
    """
    Classifies a natural-language question into a normalized GAIA task.
    
    Supported tasks:
    - 'vqa'
    - 'captioning'
    - 'grounding'
    - 'change_vqa'
    - 'optical_sar_fusion'
    - 'unknown'
    """
    
    def __init__(self):
        # Order matters! More specific tasks are checked first.
        self.rules = [
            ("optical_sar_fusion", [
                r"optical\s+(?:and|with|\+)\s+sar",
                r"sar\s+(?:and|with|\+)\s+optical",
                r"combine.*sar.*optical",
                r"combine.*optical.*sar",
                r"\bfuse\b",
                r"\bfusion\b"
            ]),
            ("change_vqa", [
                r"\bchang(?:e|es|ed)\b",
                r"\bcompar(?:e|ing)\b",
                r"\bdifferenc(?:e|es)\b",
                r"between\s+(?:these\s+)?two",
                r"\bincreased\b",
                r"\bdecreased\b"
            ]),
            ("grounding", [
                r"\bhighlight\b",
                r"show\s+me\s+where",
                r"\bwhere\s+(?:are|is)\b",
                r"\blocate\b",
                r"point\s+out",
                r"draw\s+(?:a\s+)?box",
                r"bounding\s+box"
            ]),
            ("captioning", [
                r"\bdescribe\b",
                r"\bsummarize\b",
                r"what.*\b(?:visible|seen|shown)\b",
                r"\bland\s+cover\b",
                r"\bterrain\b",
                r"\bscene\b",
                r"write\s+a\s+caption",
                r"\bcaption\b"
            ]),
            ("vqa", [
                r"^is\b",
                r"^are\b",
                r"^what\b",
                r"^how\b",
                r"^does\b",
                r"^do\b",
                r"^count\b",
                r"\bwhich\b"
            ])
        ]
        
        self.compiled_rules = [
            (task, [re.compile(pattern, re.IGNORECASE) for pattern in patterns])
            for task, patterns in self.rules
        ]

    def classify(self, question: str) -> ClassificationResult:
        """
        Classifies the given natural-language question.
        
        Args:
            question (str): The natural-language question from the user.
            
        Returns:
            ClassificationResult: The classification result containing the normalized task,
                                  a confidence value, and matched regex signals.
            
        Raises:
            TypeError: If the input is not a string.
            ValueError: If the input is an empty string after stripping.
        """
        if not isinstance(question, str):
            raise TypeError(f"Expected a string for 'question', got {type(question).__name__}")
            
        normalized_q = question.strip()
        if not normalized_q:
            raise ValueError("The question cannot be empty or just whitespace.")
            
        # Check rules in order of precedence
        for task, patterns in self.compiled_rules:
            matched = []
            for pattern in patterns:
                match = pattern.search(normalized_q)
                if match:
                    matched.append(match.group(0))
                    
            if matched:
                return ClassificationResult(
                    task=task,
                    confidence=0.9,  # High confidence for deterministic regex match
                    matched_signals=matched
                )
                
        # If no explicit patterns match, fallback to unknown
        return ClassificationResult(
            task="unknown",
            confidence=0.0,
            matched_signals=[]
        )
