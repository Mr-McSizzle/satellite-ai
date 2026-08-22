import pytest
from controller.planner import TaskPlanner

def test_vqa():
    planner = TaskPlanner()
    plan = planner.create_plan("vqa", {})
    assert plan["task"] == "vqa"
    assert len(plan["steps"]) == 1
    assert plan["steps"][0]["tool"] == "vlm"
    assert plan["steps"][0]["action"] == "answer_question"

def test_captioning():
    planner = TaskPlanner()
    plan = planner.create_plan("captioning", {})
    assert plan["task"] == "captioning"
    assert len(plan["steps"]) == 1
    assert plan["steps"][0]["tool"] == "vlm"
    assert plan["steps"][0]["action"] == "generate_caption"

def test_grounding():
    planner = TaskPlanner()
    plan = planner.create_plan("grounding", {})
    assert plan["task"] == "grounding"
    assert len(plan["steps"]) == 1
    assert plan["steps"][0]["tool"] == "vlm"
    assert plan["steps"][0]["action"] == "ground_object"

def test_change_vqa():
    planner = TaskPlanner()
    plan = planner.create_plan("change_vqa", {})
    assert plan["task"] == "change_vqa"
    assert len(plan["steps"]) == 2
    assert plan["steps"][0]["tool"] == "prithvi"
    assert plan["steps"][0]["action"] == "change_detection"
    assert plan["steps"][1]["tool"] == "vlm"
    assert plan["steps"][1]["action"] == "explain_change"

def test_optical_sar_fusion():
    planner = TaskPlanner()
    plan = planner.create_plan("optical_sar_fusion", {})
    assert plan["task"] == "optical_sar_fusion"
    assert len(plan["steps"]) == 2
    assert plan["steps"][0]["tool"] == "prithvi"
    assert plan["steps"][0]["action"] == "fusion_analysis"
    assert plan["steps"][1]["tool"] == "vlm"
    assert plan["steps"][1]["action"] == "summarize_fusion"

def test_invalid_task():
    planner = TaskPlanner()
    with pytest.raises(ValueError):
        planner.create_plan("unknown_task", {})

def test_empty_task():
    planner = TaskPlanner()
    with pytest.raises(ValueError):
        planner.create_plan("", {})
    with pytest.raises(ValueError):
        planner.create_plan(None, {})
