"""Module 07: tests for the mini server. Real files, real processes, planted secrets.

Run:  python -m pytest 07-testing-it-for-real/test_mini.py -q
"""

from __future__ import annotations

import asyncio
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import course  # noqa: E402

course.use("01", "02", "03", "04", "05", "06")
from dotenv_mini import parse  # noqa: E402
from mcp import ClientSession  # noqa: E402
from mcp.client.stdio import StdioServerParameters, stdio_client  # noqa: E402
from report_mini import RedactionError, guard, render, validate_file  # noqa: E402

SERVER = os.path.join(os.path.dirname(HERE), "06-the-mcp-wrapper", "server_mini.py")
PLANTED = {
    "a": "PLANTED-alpha-0001-zzz",
    "b": "PLANTED-bravo-0002-zzz",
    "c": "PLANTED-charlie-0003-zzz",
    "d": "PLANTED-delta-0004-zzz",
}


@pytest.fixture
def project(tmp_path):
    root = str(tmp_path / "proj")
    course.write(root, ".env", (
        f"API_SECRET={PLANTED['a']}\n"
        f"PORT={PLANTED['b']}\n"
        f"DB_URL=http://h:{PLANTED['c']}\n"
        f"junk {PLANTED['d']} junk\n"
        f"{PLANTED['d']}\n"
        f"UNCLOSED='{PLANTED['a']}\n"
    ))
    course.write(root, ".env.example", "API_SECRET=\nPORT=\nDB_URL=\n")
    course.write(root, "app.py", "import os\nos.environ['API_SECRET']\nos.environ['NEW_ONE']\n")
    return root


def test_findings_are_exact(project):
    with open(os.path.join(project, ".env"), encoding="utf-8") as fh:
        parsed = parse(fh.read())
    codes = [(f.line, f.name, f.code) for f in validate_file(parsed)]
    assert codes == [
        (2, "PORT", "bad-port"),
        (3, "DB_URL", "bad-url"),
        (4, "", "syntax"),
        (5, "", "syntax"),
        (6, "", "syntax"),
    ]


def test_no_planted_value_in_the_report(project):
    with open(os.path.join(project, ".env"), encoding="utf-8") as fh:
        parsed = parse(fh.read())
    text = guard(render(".env", validate_file(parsed)), parsed)
    for value in PLANTED.values():
        assert value not in text
    assert "PLANTED" not in text


def test_guard_catches_a_leaky_formatter(project):
    with open(os.path.join(project, ".env"), encoding="utf-8") as fh:
        parsed = parse(fh.read())
    leaky = "\n".join(f"{e.name}={e.value}" for e in parsed.entries)
    with pytest.raises(RedactionError) as ei:
        guard(leaky, parsed)
    assert PLANTED["a"] not in str(ei.value)


async def _session(root, calls):
    params = StdioServerParameters(
        command=sys.executable, args=[SERVER, "--dir", root], env={**os.environ, "PYTHONIOENCODING": "utf-8"}
    )
    results = []
    async with stdio_client(params) as (r, w), ClientSession(r, w) as s:
        await s.initialize()
        for name, args in calls:
            results.append(await s.call_tool(name, args))
    return results


def test_over_stdio_nothing_leaks_and_errors_are_clear(project):
    results = asyncio.run(_session(project, [
        ("compare_env", {}),
        ("find_usage", {}),
        ("validate_env", {}),
        ("validate_env", {"file": "../../etc/passwd"}),
    ]))
    texts = [r.content[0].text for r in results]
    assert [r.is_error for r in results] == [False, False, False, True]
    assert "used but undocumented: NEW_ONE (app.py:3)" in texts[1]
    assert "outside the sandbox folder" in texts[3]
    blob = "\n".join(texts)
    assert "PLANTED" not in blob


def test_sandbox_blocks_symlink_escape(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.env").write_bytes(f"TOKEN={PLANTED['a']}\n".encode())
    inner = tmp_path / "inner"
    inner.mkdir()
    try:
        (inner / "link.env").symlink_to(outside / "secret.env")
    except (OSError, NotImplementedError):
        pytest.skip("this machine does not allow creating symlinks")
    (res,) = asyncio.run(_session(str(inner), [("validate_env", {"file": "link.env"})]))
    assert res.is_error and "outside the sandbox folder" in res.content[0].text
    assert PLANTED["a"] not in res.content[0].text
