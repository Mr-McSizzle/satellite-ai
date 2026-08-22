"""
Root conftest.py — ensures the controller/ subdirectory is on sys.path so that
`from controller.X import ...` and `from mocks.X import ...` resolve correctly
when pytest is invoked from the repository root (e.g. `python -m pytest controller/tests`).
"""
import sys
import os

# Add controller/ to sys.path so the inner `controller` package and `mocks` package
# are resolvable as top-level when tests are run from the repository root.
_controller_root = os.path.join(os.path.dirname(__file__), "controller")
if _controller_root not in sys.path:
    sys.path.insert(0, _controller_root)
