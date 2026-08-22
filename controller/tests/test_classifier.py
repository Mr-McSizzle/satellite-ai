import pytest
from controller.classifier import QuestionClassifier, ClassificationResult

@pytest.fixture
def classifier():
    return QuestionClassifier()

def test_basic_classification(classifier):
    # VQA
    res = classifier.classify("Is there water in this image?")
    assert res.task == "vqa"
    
    # Captioning
    res = classifier.classify("Describe this satellite image.")
    assert res.task == "captioning"
    
    # Grounding
    res = classifier.classify("Highlight the water body.")
    assert res.task == "grounding"
    
    # Change VQA
    res = classifier.classify("What changed between these two images?")
    assert res.task == "change_vqa"
    
    # Optical/SAR Fusion
    res = classifier.classify("Use the optical and SAR images together.")
    assert res.task == "optical_sar_fusion"
    
    # Unknown
    res = classifier.classify("Random gibberish string.")
    assert res.task == "unknown"
    assert res.confidence == 0.0
    assert len(res.matched_signals) == 0

def test_normalization(classifier):
    # Case insensitivity
    res1 = classifier.classify("HIGHLIGHT THE WATER")
    assert res1.task == "grounding"
    
    # Whitespace padding
    res2 = classifier.classify("   Describe this image   ")
    assert res2.task == "captioning"
    
def test_invalid_input(classifier):
    # Non-string
    with pytest.raises(TypeError):
        classifier.classify(123)
        
    # Empty string
    with pytest.raises(ValueError):
        classifier.classify("")
        
    # Whitespace only
    with pytest.raises(ValueError):
        classifier.classify("   \n \t")

def test_result_structure(classifier):
    res = classifier.classify("Count the buildings.")
    # "count" -> vqa
    assert res.task == "vqa"
    assert hasattr(res, "task")
    assert hasattr(res, "confidence")
    assert hasattr(res, "matched_signals")
    assert isinstance(res.task, str)
    assert isinstance(res.confidence, float)
    assert isinstance(res.matched_signals, list)

def test_unknown_confidence_is_zero(classifier):
    res = classifier.classify("Please do something cool")
    assert res.task == "unknown"
    assert res.confidence == 0.0

def test_edge_cases_multiple_keywords(classifier):
    # "Compare the change and highlight it" -> "change_vqa" > "grounding"
    res = classifier.classify("Compare the change and highlight it")
    assert res.task == "change_vqa"
    
    # "Use optical and SAR to highlight the difference" -> "optical_sar_fusion" > "change_vqa"
    res = classifier.classify("Use optical and SAR to highlight the difference")
    assert res.task == "optical_sar_fusion"

def test_land_cover_captioning_fix(classifier):
    # The user specifically requested this to route to captioning, not vqa
    res = classifier.classify("What land cover is visible?")
    assert res.task == "captioning"
