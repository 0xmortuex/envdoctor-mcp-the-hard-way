"""Module 03: compare the sample .env with its template."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import course  # noqa: E402

course.use("01", "03")
from compare_mini import compare, render  # noqa: E402
from dotenv_mini import parse  # noqa: E402


def read(root: str, name: str) -> str:
    with open(os.path.join(root, name), encoding="utf-8") as fh:
        return fh.read()


with tempfile.TemporaryDirectory() as root:
    course.make_sample(root)
    c = compare(parse(read(root, ".env")), parse(read(root, ".env.example")))
    assert c.missing == ["UNUSED_VAR"], c.missing
    assert c.extra == ["GREETING", "REGION", "VITE_STRIPE_SECRET_KEY"], c.extra
    assert c.empty == ["EMPTY_ONE"], c.empty
    assert c.duplicated == {}
    text = render(c)
    print(text)
    assert text.splitlines() == [
        "Missing from .env (1): UNUSED_VAR",
        "Extra in .env (3): GREETING, REGION, VITE_STRIPE_SECRET_KEY",
        "Empty but required (1): EMPTY_ONE",
        "5 difference(s)",
    ]

# Duplicates and a clean file.
d = compare(parse("A=1\nB=2\nA=3\n"), parse("A=\nB=\n"))
assert d.duplicated == {"A": [1, 3]} and d.problems() == 1
assert render(compare(parse("A=1\n"), parse("A=\n"))) == "in sync"

print("module 03 ok")
