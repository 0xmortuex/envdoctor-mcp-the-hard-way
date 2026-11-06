"""Module 03: compare a real env file with its template."""

from __future__ import annotations

from dataclasses import dataclass, field

from dotenv_mini import Parsed


@dataclass
class Comparison:
    missing: list[str] = field(default_factory=list)  # in the template, absent from .env
    extra: list[str] = field(default_factory=list)  # in .env, unknown to the template
    empty: list[str] = field(default_factory=list)  # present in .env but empty
    duplicated: dict[str, list[int]] = field(default_factory=dict)  # name -> lines

    def problems(self) -> int:
        return len(self.missing) + len(self.extra) + len(self.empty) + len(self.duplicated)


def duplicates(parsed: Parsed) -> dict[str, list[int]]:
    lines: dict[str, list[int]] = {}
    for e in parsed.entries:
        lines.setdefault(e.name, []).append(e.line)
    return {n: ls for n, ls in lines.items() if len(ls) > 1}


def compare(real: Parsed, template: Parsed) -> Comparison:
    r, t = real.last(), template.last()
    out = Comparison()
    out.missing = sorted(n for n in t if n not in r)
    out.extra = sorted(n for n in r if n not in t)
    # "empty but required": the template lists it, .env has the name with no value.
    out.empty = sorted(n for n in r if n in t and r[n].value == "")
    out.duplicated = duplicates(real)
    return out


def render(c: Comparison) -> str:
    """Names and line numbers only. Module 05 explains why that is a design rule."""
    lines = []
    if c.missing:
        lines.append(f"Missing from .env ({len(c.missing)}): " + ", ".join(c.missing))
    if c.extra:
        lines.append(f"Extra in .env ({len(c.extra)}): " + ", ".join(c.extra))
    if c.empty:
        lines.append(f"Empty but required ({len(c.empty)}): " + ", ".join(c.empty))
    for name, ls in sorted(c.duplicated.items()):
        lines.append(f"Duplicated: {name} on lines {', '.join(map(str, ls))} (the last one wins)")
    lines.append("in sync" if c.problems() == 0 else f"{c.problems()} difference(s)")
    return "\n".join(lines)
