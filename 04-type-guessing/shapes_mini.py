"""Module 04: guess what a value is, and check it against what its name promises.

Every function here takes a value and returns a *description* (a type word, a fixed
message). Nothing returns, slices or quotes part of the value. That is on purpose.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

BOOLS = {"true", "false", "yes", "no", "on", "off", "1", "0"}
SCHEME = re.compile(r"^([A-Za-z][A-Za-z0-9+.\-]*)://")
DSN_SCHEMES = {"postgres", "postgresql", "mysql", "mongodb", "redis", "amqp", "sqlite"}
INT = re.compile(r"^[+-]?\d+$")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
JWT = re.compile(r"^eyJ[\w\-]+\.[\w\-]+\.[\w\-]*$")
PLACEHOLDER = re.compile(r"^(change[-_ ]?me.*|your[-_ ].*|<.*>|x{3,}|todo.*|replace[-_ ]?me.*|.*[-_ ]here)$", re.I)
SECRET_NAME = re.compile(r"(SECRET|PASSWORD|TOKEN|PRIVATE|API_?KEY|DATABASE_URL)", re.I)
CLIENT_PREFIXES = {"VITE_": "Vite", "NEXT_PUBLIC_": "Next.js", "REACT_APP_": "Create React App"}


def expected_type(name: str) -> str | None:
    """What the NAME promises. Names are convention, so this is a hint, not a rule."""
    n = name.upper()
    if n == "PORT" or n.endswith("_PORT"):
        return "port"
    if n.endswith(("_URL", "_URI", "_DSN")):
        return "url"
    if n.endswith("_EMAIL"):
        return "email"
    if n == "DEBUG" or n.startswith(("ENABLE_", "IS_", "USE_")) or n.endswith("_ENABLED"):
        return "bool"
    if n.endswith(("_TIMEOUT", "_COUNT", "_TTL")):
        return "int"
    return None


def guess_type(value: str) -> str:
    """empty, bool, int, url, dsn, email, jwt or string."""
    v = value.strip()
    if not v:
        return "empty"
    if v.lower() in BOOLS and not INT.match(v):
        return "bool"
    if INT.match(v):
        return "int"
    m = SCHEME.match(v)
    if m:
        return "dsn" if m.group(1).lower() in DSN_SCHEMES else "url"
    if JWT.match(v):
        return "jwt"
    if EMAIL.match(v):
        return "email"
    return "string"


def is_placeholder(value: str) -> bool:
    return bool(value) and PLACEHOLDER.match(value.strip()) is not None


def is_secret_name(name: str) -> bool:
    return SECRET_NAME.search(name) is not None


def check(name: str, value: str) -> list[tuple[str, str]]:
    """Problems as (code, fixed message). The message never contains the value."""
    problems: list[tuple[str, str]] = []
    if value == "":
        return [("empty", "empty value")]
    if is_placeholder(value):
        return [("placeholder", f"looks like a placeholder (length {len(value)}) that was never replaced")]
    want, got = expected_type(name), guess_type(value)
    if want == "port":
        # Never str(error): int("abc") raises "invalid literal for int(): 'abc'", which contains the value.
        if not INT.match(value.strip()):
            problems.append(("bad-port", f"name says port but the value looks like {got}"))
        elif not 1 <= int(value) <= 65535:
            problems.append(("bad-port", "port is outside 1-65535"))
    elif want == "bool" and value.strip().lower() not in BOOLS:
        problems.append(("bad-bool", f"name says boolean but the value looks like {got}"))
    elif want == "url":
        ok = got in ("url", "dsn")
        if ok:
            try:
                urlsplit(value).port  # noqa: B018  (raises ValueError for a bad port)
            except ValueError:
                ok = False  # do not use the exception text: it can embed the value
        if not ok:
            problems.append(("bad-url", "name says URL but the value does not parse as one"))
    elif want == "email" and got != "email":
        problems.append(("bad-email", f"name says email but the value looks like {got}"))
    for prefix, framework in CLIENT_PREFIXES.items():
        if name.startswith(prefix) and is_secret_name(name):
            problems.append(("client-exposed-secret", f"{framework} inlines {prefix}* variables into the browser bundle"))
    return problems
