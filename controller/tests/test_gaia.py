import pytest
from controller.gaia import GaiaController
from mocks.mock_vlm import MockVLM
from mocks.mock_prithvi import MockPrithvi

@pytest.fixture
def controller():
    return GaiaController(vlm=MockVLM(), prithvi=MockPrithvi())

def make_request(question, num_images=1, mod="optical", fail_vlm=False, fail_prithvi=False):
    req = {
        "question": question,
        "images": []
    }
    for i in range(num_images):
        req["images"].append({
            "reference": f"img{i}.tif",
            "format": "tiff",
            "modality": mod,
            "acquisition_time": f"2023-01-0{i+1}T00:00:00Z"
        })
    if fail_vlm:
        req["fail_vlm"] = True
    if fail_prithvi:
        req["fail_prithvi"] = True
    return req

def test_simple_vqa(controller):
    req = make_request("Is there water in this image?", 1)
    res = controller.run(req)
    
    assert res["task"] == "vqa"
    assert res["execution_trace"]["execution_status"] == "success"
    assert len(res["execution_trace"]["tools_invoked"]) == 1
    assert res["execution_trace"]["tools_invoked"][0]["tool_name"] == "vlm"

def test_captioning(controller):
    req = make_request("Describe this satellite image.", 1)
    res = controller.run(req)
    
    assert res["task"] == "captioning"
    assert res["execution_trace"]["execution_status"] == "success"
    assert len(res["execution_trace"]["tools_invoked"]) == 1
    assert res["execution_trace"]["tools_invoked"][0]["tool_name"] == "vlm"

def test_grounding(controller):
    req = make_request("Highlight the water body.", 1)
    res = controller.run(req)
    
    assert res["task"] == "grounding"
    assert res["execution_trace"]["execution_status"] == "success"
    assert len(res["execution_trace"]["tools_invoked"]) == 1
    assert res["execution_trace"]["tools_invoked"][0]["tool_name"] == "vlm"

def test_change_vqa(controller):
    req = make_request("What changed between these two images?", 2)
    res = controller.run(req)
    
    assert res["task"] == "change_vqa"
    assert res["execution_trace"]["execution_status"] == "success"
    assert len(res["execution_trace"]["tools_invoked"]) == 2
    assert res["execution_trace"]["tools_invoked"][0]["tool_name"] == "prithvi"
    assert res["execution_trace"]["tools_invoked"][1]["tool_name"] == "vlm"

def test_optical_sar_fusion(controller):
    req = make_request("Use the optical and SAR images together.", 2)
    # Ensure one is SAR and one is optical to pass validation
    req["images"][0]["modality"] = "optical"
    req["images"][1]["modality"] = "sar"
    
    res = controller.run(req)
    
    assert res["task"] == "optical_sar_fusion"
    assert res["execution_trace"]["execution_status"] == "success"
    assert len(res["execution_trace"]["tools_invoked"]) == 2
    assert res["execution_trace"]["tools_invoked"][0]["tool_name"] == "prithvi"
    assert res["execution_trace"]["tools_invoked"][1]["tool_name"] == "vlm"

def test_invalid_input(controller):
    # Change VQA but only 1 image provided
    req = make_request("What changed between these two images?", 1)
    res = controller.run(req)
    
    assert res["task"] == "change_vqa"
    assert res["execution_trace"]["execution_status"] == "failed"
    assert len(res["execution_trace"]["tools_invoked"]) == 0
    assert not res["execution_trace"]["validation_result"]["valid"]
    assert any("exactly 2 images" in err for err in res["execution_trace"]["validation_result"]["errors"])

def test_unknown_question(controller):
    req = make_request("Gibberish string here", 1)
    res = controller.run(req)
    
    assert res["task"] == "unknown"
    assert res["execution_trace"]["execution_status"] == "failed"
    assert not res["execution_trace"]["validation_result"]["valid"]

def test_prithvi_failure(controller):
    req = make_request("What changed between these two images?", 2, fail_prithvi=True)
    res = controller.run(req)
    
    assert res["task"] == "change_vqa"
    assert res["execution_trace"]["execution_status"] == "failed"
    assert len(res["execution_trace"]["tools_invoked"]) == 1
    assert res["execution_trace"]["tools_invoked"][0]["tool_name"] == "prithvi"
    assert res["execution_trace"]["tools_invoked"][0]["execution_status"] == "failed"

def test_vlm_failure(controller):
    req = make_request("Is there water in this image?", 1, fail_vlm=True)
    res = controller.run(req)
    
    assert res["task"] == "vqa"
    assert res["execution_trace"]["execution_status"] == "failed"
    assert len(res["execution_trace"]["tools_invoked"]) == 1
    assert res["execution_trace"]["tools_invoked"][0]["tool_name"] == "vlm"
    assert res["execution_trace"]["tools_invoked"][0]["execution_status"] == "failed"
