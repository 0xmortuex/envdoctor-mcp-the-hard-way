"""Shared plumbing for the course: module imports and the sample project.

Each module adds one file. A module's main.py calls ``use("01", "02")`` to put the earlier
modules' folders on sys.path, then imports their code like normal modules.
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Fake values. Every one is unique and obviously fake, so a leak is a plain substring search.
SECRETS = {
    "stripe": "FAKE-stripe-key-0f9e8d7c6b5a",
    "dbpass": "FAKE-db-password-7a6b5c",
    "session": "FAKE-session-secret-123456",
}


def use(*prefixes: str) -> None:
    """Put the module folders whose names start with these prefixes on sys.path."""
    for prefix in prefixes:
        matches = [d for d in sorted(os.listdir(ROOT)) if d.startswith(prefix) and os.path.isdir(os.path.join(ROOT, d))]
        if not matches:
            raise SystemExit(f"no module folder starts with {prefix!r}")
        path = os.path.join(ROOT, matches[0])
        if path not in sys.path:
            sys.path.insert(0, path)


def write(root: str, rel: str, text: str) -> None:
    path = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:  # bytes: no newline translation on Windows
        fh.write(text.encode("utf-8"))


def make_sample(root: str) -> str:
    """A small realistic project. Returns ``root``."""
    s = SECRETS
    write(root, ".env", (
        "# local development\n"
        f"STRIPE_SECRET_KEY={s['stripe']}\n"
        f"DATABASE_URL=postgres://app:{s['dbpass']}@localhost:5432/app\n"
        "PORT=99999\n"
        "DEBUG=maybe\n"
        f'SESSION_SECRET="{s["session"]}"\n'
        "API_URL=https://api.example.test\n"
        f"VITE_STRIPE_SECRET_KEY={s['stripe']}\n"
        "EMPTY_ONE=\n"
        "export REGION=eu-west-1\n"
        'GREETING="hello ${REGION}"\n'
    ))
    write(root, ".env.example", (
        "STRIPE_SECRET_KEY=\n"
        "DATABASE_URL=\n"
        "PORT=3000\n"
        "DEBUG=false\n"
        "SESSION_SECRET=\n"
        "API_URL=\n"
        "EMPTY_ONE=\n"
        "UNUSED_VAR=\n"
    ))
    write(root, "src/app.py", (
        "import os\n"
        "db = os.environ['DATABASE_URL']\n"
        "port = os.getenv('PORT', '3000')\n"
        "dsn = os.environ.get('SENTRY_DSN')\n"
    ))
    write(root, "web/main.ts", (
        "const api = import.meta.env.VITE_API_URL;\n"
        "const k = import.meta.env.VITE_STRIPE_SECRET_KEY;\n"
        "const server = process.env.API_URL;\n"
    ))
    return root
