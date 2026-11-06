"""Module 06: wrap the engine in an MCP server with a sandbox and good errors.

Run it:  python server_mini.py --dir /path/to/project
"""

from __future__ import annotations

import argparse
import functools
import os
import sys
from collections.abc import Callable
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import course  # noqa: E402

course.use("01", "02", "03", "04", "05")
from compare_mini import compare, render as render_compare  # noqa: E402
from dotenv_mini import parse  # noqa: E402
from mcp.server.mcpserver import MCPServer  # noqa: E402
from mcp.server.mcpserver.exceptions import ToolError  # noqa: E402
from report_mini import guard, render, validate_file  # noqa: E402
from scan_mini import cross_check, scan_tree  # noqa: E402

mcp = MCPServer(
    "envdoctor-mini",
    instructions="Diagnose environment variables. Read-only; values are never shown, only names and line numbers.",
)
ROOT = os.getcwd()


class UserError(Exception):
    """A problem the agent can act on. Its message is safe to show."""


def tool(fn: Callable[..., str]) -> Callable[..., str]:
    """Register `fn` as an MCP tool, turning UserError into the one thing mcp>=2 shows clients: a ToolError."""

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        try:
            return fn(*args, **kwargs)
        except UserError as e:
            raise ToolError(str(e)) from e

    mcp.tool()(wrapper)
    return fn


def resolve(rel: str) -> str:
    """Resolve a path inside the sandbox, or refuse. realpath follows symlinks, so a link cannot escape."""
    full = os.path.realpath(os.path.join(ROOT, rel))
    if os.path.commonpath([ROOT, full]) != ROOT:
        raise UserError(f"{rel!r} is outside the sandbox folder (the server was started with --dir)")
    if not os.path.exists(full):
        raise UserError(f"{rel!r} does not exist inside the sandbox folder")
    return full


def read_env(rel: str):  # type: ignore[no-untyped-def]
    with open(resolve(rel), encoding="utf-8", errors="replace") as fh:
        return parse(fh.read())


@tool
def compare_env(file: str = ".env", against: str = ".env.example") -> str:
    """Compare an env file with its template: names missing, extra, empty-but-required, duplicated.
    Values are never shown. file/against are paths relative to the sandbox folder."""
    return render_compare(compare(read_env(file), read_env(against)))


@tool
def find_usage(path: str = ".", template: str = ".env.example") -> str:
    """Scan source under `path` for environment reads and report variables used in code but
    missing from the template, and documented but never read. Includes file:line."""
    usage = scan_tree(resolve(path))
    documented = {e.name for e in read_env(template).entries}
    undocumented, unused = cross_check({u.name for u in usage}, documented)
    lines = []
    for n in undocumented:
        first = next(u for u in usage if u.name == n)
        lines.append(f"used but undocumented: {n} ({first.file}:{first.line})")
    if unused:
        lines.append("documented but never read: " + ", ".join(unused))
    return "\n".join(lines) or "every variable read by the code is documented"


@tool
def validate_env(file: str = ".env") -> str:
    """Check an env file for syntax errors, placeholders, bad ports/URLs/booleans and secrets
    that a bundler would expose to the browser. Reports names, lines and fixed messages only."""
    parsed = read_env(file)
    return guard(render(file, validate_file(parsed)), parsed)


def main() -> None:
    global ROOT
    ap = argparse.ArgumentParser(prog="envdoctor-mini")
    ap.add_argument("--dir", default=".", help="sandbox folder: the server reads nothing outside it")
    args = ap.parse_args()
    if not os.path.isdir(args.dir):
        ap.error(f"--dir {args.dir!r} is not a directory")
    ROOT = os.path.realpath(args.dir)
    mcp.run()


if __name__ == "__main__":
    main()
