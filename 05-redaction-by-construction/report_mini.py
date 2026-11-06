"""Module 05: reports that cannot contain a value, plus a trip-wire in case they ever do.

"By construction" means the leak is not prevented by remembering to redact. It is
prevented because the data structure has nowhere to put a value:

* ``Finding`` has name, line, code, message. There is no ``value`` field.
* ``message`` comes from ``shapes_mini.check``, whose messages are fixed phrases.
* ``Parsed.errors`` holds a line number and a fixed phrase, never the line's text.
"""

from __future__ import annotations

from dataclasses import dataclass

from dotenv_mini import Parsed
from shapes_mini import check, is_secret_name


class RedactionError(Exception):
    """Raised when a report would have contained a secret. The message never does."""


@dataclass(frozen=True)
class Finding:
    name: str
    line: int
    code: str
    message: str


def validate_file(parsed: Parsed) -> list[Finding]:
    out = [Finding("", line, "syntax", msg) for line, msg in parsed.errors]
    for e in parsed.entries:
        out.extend(Finding(e.name, e.line, code, msg) for code, msg in check(e.name, e.value))
    return sorted(out, key=lambda f: (f.line, f.code))


def render(rel: str, findings: list[Finding]) -> str:
    lines = [f"== {rel} =="]
    for f in findings:
        who = f" {f.name}" if f.name else ""
        lines.append(f"  line {f.line}{who}: {f.code} - {f.message}")
    if not findings:
        lines.append("  no problems found")
    return "\n".join(lines)


def guard(text: str, parsed: Parsed) -> str:
    """Last line of defence. If a secret-looking variable's value is in `text`, refuse.

    Only secret-looking names are checked: a short value like "production" would
    match ordinary words in the report (file names, messages) and cause false alarms.
    """
    for e in parsed.entries:
        if e.value and len(e.value) >= 6 and is_secret_name(e.name) and e.value in text:
            raise RedactionError(f"report for {e.name} (line {e.line}) contained its value; output withheld")
    return text
