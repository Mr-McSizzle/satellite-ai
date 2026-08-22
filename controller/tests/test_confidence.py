import pytest
from controller.confidence import ConfidenceEngine

def test_high_confidence():
    engine = ConfidenceEngine()
    res = engine.calculate({"tool_confidences": [0.9, 0.95], "validation_valid": True, "evidence_available": True})
    assert res["confidence"] >= 0.8
    assert res["level"] == "high"

def test_medium_confidence():
    engine = ConfidenceEngine()
    res = engine.calculate({"tool_confidences": [0.6, 0.6], "validation_valid": True, "evidence_available": True})
    assert 0.5 <= res["confidence"] < 0.8
    assert res["level"] == "medium"

def test_low_confidence():
    engine = ConfidenceEngine()
    res = engine.calculate({"tool_confidences": [0.4], "validation_valid": True, "evidence_available": True})
    assert res["confidence"] < 0.5
    assert res["level"] == "low"

def test_invalid_validation_reduces_score():
    engine = ConfidenceEngine()
    # base 1.0, -0.3 => 0.7
    res = engine.calculate({"tool_confidences": [1.0], "validation_valid": False, "evidence_available": True})
    assert abs(res["confidence"] - 0.7) < 1e-6
    assert res["level"] == "medium"

def test_missing_evidence_reduces_score():
    engine = ConfidenceEngine()
    # base 1.0, -0.2 => 0.8
    res = engine.calculate({"tool_confidences": [1.0], "validation_valid": True, "evidence_available": False})
    assert abs(res["confidence"] - 0.8) < 1e-6
    assert res["level"] == "high"

def test_score_never_exceeds_one():
    engine = ConfidenceEngine()
    # If base score starts very high, ensure it clamps to 1.0
    res = engine.calculate({"tool_confidences": [1.5], "validation_valid": True, "evidence_available": True})
    assert res["confidence"] == 1.0
    assert res["level"] == "high"

def test_score_never_goes_below_zero():
    engine = ConfidenceEngine()
    res = engine.calculate({"tool_confidences": [0.1], "validation_valid": False, "evidence_available": False})
    assert res["confidence"] == 0.0
    assert res["level"] == "low"
