"""Run every module's main.py, the way CI does.

Each main.py checks its own results with assert, so a chapter whose code drifts out of
sync with what its README claims fails here.

Usage: python verify.py            # all modules
       python verify.py 02 05      # just these
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))


def run_module(name: str) -> tuple[bool, str, float]:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    start = time.monotonic()
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, name, "main.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=300, cwd=ROOT,
    )  # fmt: skip
    return proc.returncode == 0, proc.stdout + proc.stderr, time.monotonic() - start


def main() -> int:
    wanted = sys.argv[1:]
    modules = sorted(
        d for d in os.listdir(ROOT)
        if os.path.isfile(os.path.join(ROOT, d, "main.py"))
        and (not wanted or any(d.startswith(w) for w in wanted))
    )
    if not modules:
        print("no modules matched")
        return 1
    failed = []
    for m in modules:
        ok, output, secs = run_module(m)
        print(f"{'PASS' if ok else 'FAIL'}  {m}  ({secs:.1f}s)")
        if not ok:
            failed.append(m)
            print("    " + output.strip().replace("\n", "\n    "))
    print(f"\n{len(modules) - len(failed)}/{len(modules)} modules verified")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
