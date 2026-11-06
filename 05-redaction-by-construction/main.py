"""Module 05: prove the report holds no value, then prove the guard catches a sabotaged one."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import course  # noqa: E402

course.use("01", "04", "05")
from dotenv_mini import parse  # noqa: E402
from report_mini import Finding, RedactionError, guard, render, validate_file  # noqa: E402

HOSTILE = (
    f"STRIPE_SECRET_KEY={course.SECRETS['stripe']}\n"
    "PORT=99999\n"
    f"API_URL=http://host:{course.SECRETS['dbpass']}\n"
    f"this line has {course.SECRETS['session']} and is not an assignment\n"
    f"{course.SECRETS['session']}\n"                      # a secret pasted on its own line
    f"BROKEN='{course.SECRETS['stripe']}\n"               # never closed
)

parsed = parse(HOSTILE)
findings = validate_file(parsed)
text = guard(render(".env", findings), parsed)
print(text)
for secret in course.SECRETS.values():
    assert secret not in text, secret
assert "FAKE" not in text  # not even a fragment

# The report still says something useful: redaction is not "report nothing".
codes = [(f.line, f.code) for f in findings]
assert (2, "bad-port") in codes and (3, "bad-url") in codes
assert (4, "syntax") in codes and (5, "syntax") in codes and (6, "syntax") in codes

# Finding has nowhere to put a value:
assert [f for f in Finding.__dataclass_fields__] == ["name", "line", "code", "message"]

# Sabotage: a "helpful" formatter that quotes the offending value, the way most people write it first.
def leaky_render(parsed_file):
    return "\n".join(f"{e.name} is invalid: {e.value!r}" for e in parsed_file.entries)


leaky = leaky_render(parsed)
assert course.SECRETS["stripe"] in leaky  # it really leaks...
try:
    guard(leaky, parsed)
except RedactionError as e:
    assert course.SECRETS["stripe"] not in str(e)  # ...and the guard's own error does not
    print("guard tripped:", e)
else:
    raise AssertionError("the guard should have refused the leaky report")

# Fixture on disk, to be sure about newlines and encodings:
with tempfile.TemporaryDirectory() as root:
    course.make_sample(root)
    with open(os.path.join(root, ".env"), encoding="utf-8") as fh:
        sample = parse(fh.read())
    out = guard(render(".env", validate_file(sample)), sample)
    assert all(s not in out for s in course.SECRETS.values())

print("module 05 ok")
