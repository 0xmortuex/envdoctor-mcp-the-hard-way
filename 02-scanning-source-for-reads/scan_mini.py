"""Module 02: find environment reads in source code, in several languages."""

from __future__ import annotations

import bisect
import os
import re
from dataclasses import dataclass

ID = r"([A-Za-z_][A-Za-z0-9_]*)"
QID = r"""\s*['"`]""" + ID + r"""['"`]"""

# One list of regexes per language family. Group 1 is always the variable name.
PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "js": [
        re.compile(r"process\.env\." + ID),
        re.compile(r"process\.env\[" + QID + r"\s*\]"),
        re.compile(r"import\.meta\.env\." + ID),
    ],
    "py": [
        re.compile(r"os\.environ\[" + QID + r"\s*\]"),
        re.compile(r"os\.environ\.get\(" + QID),
        re.compile(r"os\.getenv\(" + QID),
    ],
    "rb": [re.compile(r"\bENV\[" + QID + r"\s*\]"), re.compile(r"\bENV\.fetch\(" + QID)],
    "rs": [re.compile(r"\benv::var(?:_os)?\(\s*\"" + ID + r"\"")],
    "go": [re.compile(r"\bos\.(?:Getenv|LookupEnv)\(\s*\"" + ID + r"\"")],
    "jvm": [re.compile(r"System\.getenv\(\s*\"" + ID + r"\"")],
}
EXT = {
    ".js": "js", ".ts": "js", ".tsx": "js", ".mjs": "js", ".vue": "js",
    ".py": "py", ".rb": "rb", ".rs": "rs", ".go": "go", ".java": "jvm", ".kt": "jvm",
}  # fmt: skip
# `const { A, B: renamed = 1, ...rest } = process.env` reads A and B without ever writing process.env.A
DESTRUCTURE = re.compile(r"\{([^{}]*)\}\s*=\s*(?:process\.env|import\.meta\.env)\b")
# Names Vite always provides; they are not configuration.
VITE_BUILTINS = {"MODE", "BASE_URL", "PROD", "DEV", "SSR"}
# Variables every process has. Reporting them as "undocumented" would be noise.
AMBIENT = {"PATH", "HOME", "USER", "PWD", "SHELL", "TERM", "LANG", "TMPDIR", "TEMP", "NODE_ENV", "CI"}
PRUNE = {".git", "node_modules", "__pycache__", "dist", "build", ".venv", "venv", "target", "vendor"}


@dataclass(frozen=True)
class Usage:
    name: str
    file: str
    line: int


def scan_text(text: str, lang: str, rel: str) -> list[Usage]:
    starts = [0] + [m.end() for m in re.finditer("\n", text)]  # offset of each line start

    def line_of(pos: int) -> int:
        return bisect.bisect_right(starts, pos)  # the line containing offset `pos`

    found = []
    for pat in PATTERNS[lang]:
        for m in pat.finditer(text):
            if pat.pattern.startswith("import") and m.group(1) in VITE_BUILTINS:
                continue
            found.append(Usage(m.group(1), rel, line_of(m.start())))
    if lang == "js":
        for m in DESTRUCTURE.finditer(text):
            for part in m.group(1).split(","):
                nm = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)", part)
                if nm and not part.strip().startswith("..."):
                    found.append(Usage(nm.group(1), rel, line_of(m.start())))
    return found


def scan_tree(root: str) -> list[Usage]:
    found: list[Usage] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d not in PRUNE)
        for fn in sorted(filenames):
            lang = EXT.get(os.path.splitext(fn)[1].lower())
            if not lang:
                continue
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8", errors="replace") as fh:
                rel = os.path.relpath(path, root).replace(os.sep, "/")
                found.extend(scan_text(fh.read(), lang, rel))
    return sorted(set(found), key=lambda u: (u.file, u.line, u.name))


def cross_check(used: set[str], documented: set[str]) -> tuple[list[str], list[str]]:
    """(used but undocumented, documented but unused), both sorted."""
    undocumented = sorted(n for n in used - documented if n not in AMBIENT)
    unused = sorted(documented - used)
    return undocumented, unused
