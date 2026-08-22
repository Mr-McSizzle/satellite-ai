with open("tests/test_gaia.py", "r") as f:
    content = f.read()

# Let's just fix test_invalid_input specifically
# It currently has: assert any("Planning error" in err for err in res["execution_trace"]["errors"])
# followed by: assert any("exactly 2 images" in err ...

# Wait, let's just fetch the file and look at it to be sure
