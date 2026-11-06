"""Module 01: a dotenv parser, small enough to read in one sitting.

The rules below are the ones python-dotenv implements. main.py checks them against
python-dotenv itself.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_.\-]*")
EXPORT = re.compile(r"export[ \t]+")
EXPAND = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?:(:?-)([^}]*))?\}")
INLINE_COMMENT = re.compile(r"\s+#.*")
ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'", "$": "$"}


@dataclass
class Entry:
    name: str
    line: int
    # repr=False: if somebody prints an Entry while debugging, the value stays out of the log.
    value: str = field(repr=False)
    quote: str = ""


@dataclass
class Parsed:
    entries: list[Entry] = field(default_factory=list)
    # (line number, fixed message). Never any text from the file: see module 05.
    errors: list[tuple[int, str]] = field(default_factory=list)

    def last(self) -> dict[str, Entry]:
        return {e.name: e for e in self.entries}  # later entries overwrite earlier ones


def find_closing_quote(body: str, quote: str) -> int:
    i = 0
    while i < len(body):
        if body[i] == "\\" and i + 1 < len(body):
            i += 2  # skip the escaped character, whatever it is
            continue
        if body[i] == quote:
            return i
        i += 1
    return -1


def unescape(body: str, quote: str) -> str:
    out: list[str] = []
    i = 0
    allowed = ESCAPES if quote == '"' else {"'": "'", "\\": "\\"}  # single quotes are almost literal
    while i < len(body):
        if body[i] == "\\" and i + 1 < len(body) and body[i + 1] in allowed:
            out.append(allowed[body[i + 1]])
            i += 2
        else:
            out.append(body[i])
            i += 1
    return "".join(out)


def expand(value: str, env: dict[str, str]) -> str:
    def sub(m: re.Match[str]) -> str:
        name, op, default = m.group(1), m.group(2), m.group(3)
        if name in env:
            return env[name]
        return (default or "") if op else ""

    return EXPAND.sub(sub, value)


def parse(text: str) -> Parsed:
    out = Parsed()
    env: dict[str, str] = {}
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        lineno = i + 1
        raw = lines[i]
        i += 1
        line = raw[:-1] if raw.endswith("\r") else raw  # tolerate CRLF files
        if not line.strip() or line.strip().startswith("#"):
            continue
        s = line.lstrip()
        m = EXPORT.match(s)
        if m:
            s = s[m.end():]
        km = KEY.match(s)
        if not km:
            out.errors.append((lineno, "not a KEY=value assignment"))
            continue
        rest = s[km.end():].lstrip(" \t")
        if not rest.startswith("="):
            # A line holding a single bare word might be a secret pasted on its own,
            # so we report the line number and never keep the word.
            out.errors.append((lineno, "no '=' after the name"))
            continue
        v = rest[1:].lstrip(" \t")
        if v[:1] in ("'", '"'):
            quote = v[0]
            buf = v[1:]
            end = find_closing_quote(buf, quote)
            while end < 0 and i < len(lines):  # quoted values may span lines
                buf += "\n" + lines[i]
                i += 1
                end = find_closing_quote(buf, quote)
            if end < 0:
                out.errors.append((lineno, "unterminated quoted value"))
                continue
            tail = buf[end + 1:].strip()
            if tail and not tail.startswith("#"):
                out.errors.append((lineno, "unexpected text after the closing quote"))
                continue
            value = expand(unescape(buf[:end], quote), env)
        else:
            value = expand(INLINE_COMMENT.sub("", v).rstrip(), env)
            quote = ""
        out.entries.append(Entry(km.group(0), lineno, value, quote))
        env[km.group(0)] = value
    return out
