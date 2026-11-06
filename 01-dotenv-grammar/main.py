"""Module 01: parse dotenv text and prove it matches python-dotenv."""

import io
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import course  # noqa: E402

course.use("01")
from dotenv import dotenv_values  # noqa: E402

from dotenv_mini import parse  # noqa: E402

CORPUS = [
    "A=1\n",
    "A = 1\n",
    "export A=1\n",
    "A=\n",
    "A=hello world\n",
    "A=hello   # trailing comment\n",
    "A=hello#not-a-comment\n",
    "A='single # not a comment'\n",
    'A="double # not a comment"\n',
    'A="line1\\nline2"\n',
    "A='line1\\nline2'\n",
    'A="say \\"hi\\""\n',
    'A="multi\nline\nvalue"\n',
    "A=1\nA=2\n",
    "A=1\r\nB=2\r\n",
    "A=a=b=c\n",
    "A=C:\\path\\file\n",
]

for text in CORPUS:
    expected = dict(dotenv_values(stream=io.StringIO(text), interpolate=False))
    got = {e.name: e.value for e in parse(text).entries}
    assert got == expected, (text, got, expected)
print(f"{len(CORPUS)} snippets parse exactly like python-dotenv")

# Expansion: ${VAR} resolves against earlier variables of the SAME file.
text = "BASE=/srv\nDIR=${BASE}/app\nDEF=${NOPE_X:-fallback}\n"
parsed = parse(text)
assert parsed.last()["DIR"].value == "/srv/app"
assert parsed.last()["DEF"].value == "fallback"
assert {e.name: e.value for e in parsed.entries} == dict(dotenv_values(stream=io.StringIO(text), interpolate=True))

# Duplicates keep every entry; the last one wins.
dup = parse("A=1\nB=x\nA=2\n")
assert [e.line for e in dup.entries if e.name == "A"] == [1, 3]
assert dup.last()["A"].value == "2"

# Errors carry a line number and a fixed phrase, never the text.
bad = parse("good=1\nthis line has FAKE_SECRET_XYZ in it\nK='unterminated FAKE_SECRET_XYZ\n")
assert bad.errors == [(2, "no '=' after the name"), (3, "unterminated quoted value")]
assert all("FAKE_SECRET_XYZ" not in msg for _, msg in bad.errors)

# repr() of an entry does not show the value.
assert "hunter2" not in repr(parse("PASSWORD=hunter2\n").entries[0])

# And on a real file on disk:
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, ".env")
    with open(path, "wb") as fh:
        fh.write(b"# comment\nexport REGION=eu-west-1\nGREETING=\"hello ${REGION}\"\n")
    with open(path, encoding="utf-8") as fh:
        p = parse(fh.read())
    assert [(e.name, e.value) for e in p.entries] == [("REGION", "eu-west-1"), ("GREETING", "hello eu-west-1")]

print("module 01 ok")
