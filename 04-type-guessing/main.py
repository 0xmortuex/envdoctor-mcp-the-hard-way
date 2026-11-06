"""Module 04: type guessing and shape checks on the sample project."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import course  # noqa: E402

course.use("01", "04")
from dotenv_mini import parse  # noqa: E402
from shapes_mini import check, guess_type, is_placeholder  # noqa: E402

GUESSES = {
    "": "empty",
    "true": "bool",
    "42": "int",
    "1": "int",  # ambiguous: could be a bool, so the name decides (see `check`)
    "https://example.test/x": "url",
    "postgres://u:p@h:5432/db": "dsn",
    "a@b.io": "email",
    "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.sig_-": "jwt",
    "hello": "string",
}
for value, expected in GUESSES.items():
    assert guess_type(value) == expected, (value, guess_type(value))
print(f"{len(GUESSES)} value shapes guessed correctly")

for value in ("changeme", "your_api_key_here", "<token>", "xxxx", "TODO"):
    assert is_placeholder(value), value
for value in ("production", "3000", "https://api.example.test"):
    assert not is_placeholder(value), value

assert check("PORT", "70000") == [("bad-port", "port is outside 1-65535")]
assert check("DB_PORT", "five")[0][0] == "bad-port"
assert check("DEBUG", "maybe")[0][0] == "bad-bool"
assert check("DEBUG", "off") == []
assert check("API_URL", "not a url")[0][0] == "bad-url"
assert check("API_URL", "http://host:abc/")[0][0] == "bad-url"  # urlsplit raises here; we do not echo it
assert check("API_TOKEN", "changeme")[0][0] == "placeholder"
assert check("VITE_AUTH_TOKEN", "abc123")[0][0] == "client-exposed-secret"

# No message may contain the value, even when the library error would have.
secret = "FAKE-SHAPE-VALUE-991"
for name in ("PORT", "DEBUG", "API_URL", "X_EMAIL", "VITE_SECRET_KEY"):
    for _code, message in check(name, secret) + check(name, "http://h:" + secret):
        assert secret not in message, (name, message)

# On the sample project:
with tempfile.TemporaryDirectory() as root:
    course.make_sample(root)
    with open(os.path.join(root, ".env"), encoding="utf-8") as fh:
        entries = parse(fh.read()).entries
    found = {e.name: check(e.name, e.value) for e in entries if check(e.name, e.value)}
    assert sorted(found) == ["DEBUG", "EMPTY_ONE", "PORT", "VITE_STRIPE_SECRET_KEY"], sorted(found)
    for name, problems in sorted(found.items()):
        for code, message in problems:
            print(f"{name}: {code} - {message}")

print("module 04 ok")
