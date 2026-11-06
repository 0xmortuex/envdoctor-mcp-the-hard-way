"""Module 07: run the test suite for real."""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
proc = subprocess.run(
    [sys.executable, "-m", "pytest", os.path.join(HERE, "test_mini.py"), "-q", "-p", "no:cacheprovider"],
    capture_output=True, text=True, env=env, timeout=300,
)  # fmt: skip
print(proc.stdout)
print(proc.stderr)
assert proc.returncode == 0, "the module-07 tests failed"
assert " passed" in proc.stdout and "failed" not in proc.stdout
print("module 07 ok")
