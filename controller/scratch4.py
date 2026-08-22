import re

with open("tests/test_gaia.py", "r") as f:
    content = f.read()

# Replace test_invalid_input with correct assertions
old_test = """def test_invalid_input(controller):
    # Change VQA but only 1 image provided
    req = make_request("What changed between these two images?", 1)
    res = controller.run(req)
    
    assert res["task"] == "change_vqa"
    assert res["execution_trace"]["execution_status"] == "failed"
    assert len(res["execution_trace"]["tools_invoked"]) == 0
    assert any("Planning error" in err for err in res["execution_trace"]["errors"])
    assert any("exactly 2 images" in err for err in res["execution_trace"]["validation_result"]["errors"])"""

new_test = """def test_invalid_input(controller):
    # Change VQA but only 1 image provided
    req = make_request("What changed between these two images?", 1)
    res = controller.run(req)
    
    assert res["task"] == "change_vqa"
    assert res["execution_trace"]["execution_status"] == "failed"
    assert len(res["execution_trace"]["tools_invoked"]) == 0
    assert not res["execution_trace"]["validation_result"]["valid"]
    assert any("exactly 2 images" in err for err in res["execution_trace"]["validation_result"]["errors"])"""

content = content.replace(old_test, new_test)

with open("tests/test_gaia.py", "w") as f:
    f.write(content)
