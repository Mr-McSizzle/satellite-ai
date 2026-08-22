with open("tests/test_gaia.py", "r") as f:
    content = f.read()

# Replace the assertion in test_unknown_question
content = content.replace(
    'assert not res["execution_trace"]["validation_result"]["valid"]',
    'assert any("Planning error" in err for err in res["execution_trace"]["errors"])'
)

with open("tests/test_gaia.py", "w") as f:
    f.write(content)
