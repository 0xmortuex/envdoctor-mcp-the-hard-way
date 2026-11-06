"""Module 02: scan a sample project for environment reads and cross-check the template."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import course  # noqa: E402

course.use("01", "02")
from dotenv_mini import parse  # noqa: E402
from scan_mini import cross_check, scan_text, scan_tree  # noqa: E402

# One snippet per language.
SNIPPETS = {
    "js": ("a.ts", "process.env.A_ONE;\nprocess.env['B_TWO'];\nimport.meta.env.VITE_THREE;\nimport.meta.env.MODE;\n"
           "const { D_FOUR, E_FIVE: alias = 'x', ...rest } = process.env;\n",
           [("A_ONE", 1), ("B_TWO", 2), ("D_FOUR", 5), ("E_FIVE", 5), ("VITE_THREE", 3)]),
    "py": ("a.py", "import os\nos.environ['P1']\nos.environ.get('P2', 'd')\nos.getenv(\"P3\")\n",
           [("P1", 2), ("P2", 3), ("P3", 4)]),
    "rb": ("a.rb", "ENV['R1']\nENV.fetch('R2', 'x')\n", [("R1", 1), ("R2", 2)]),
    "rs": ("a.rs", 'let a = std::env::var("S1");\nlet b = env::var_os("S2");\n', [("S1", 1), ("S2", 2)]),
    "go": ("a.go", 'a := os.Getenv("G1")\nb, ok := os.LookupEnv("G2")\n', [("G1", 1), ("G2", 2)]),
    "jvm": ("A.java", 'String s = System.getenv("J1");\n', [("J1", 1)]),
}
for lang, (name, text, expected) in SNIPPETS.items():
    got = sorted((u.name, u.line) for u in scan_text(text, lang, name))
    assert got == expected, (lang, got, expected)
print(f"{len(SNIPPETS)} language families scanned correctly")

with tempfile.TemporaryDirectory() as root:
    course.make_sample(root)
    usage = scan_tree(root)
    assert [(u.name, u.file, u.line) for u in usage] == [
        ("DATABASE_URL", "src/app.py", 2),
        ("PORT", "src/app.py", 3),
        ("SENTRY_DSN", "src/app.py", 4),
        ("VITE_API_URL", "web/main.ts", 1),
        ("VITE_STRIPE_SECRET_KEY", "web/main.ts", 2),
        ("API_URL", "web/main.ts", 3),
    ], usage

    with open(os.path.join(root, ".env.example"), encoding="utf-8") as fh:
        documented = {e.name for e in parse(fh.read()).entries}
    undocumented, unused = cross_check({u.name for u in usage}, documented)
    assert undocumented == ["SENTRY_DSN", "VITE_API_URL", "VITE_STRIPE_SECRET_KEY"], undocumented
    assert unused == ["DEBUG", "EMPTY_ONE", "SESSION_SECRET", "STRIPE_SECRET_KEY", "UNUSED_VAR"], unused
    for n in undocumented:
        first = next(u for u in usage if u.name == n)
        print(f"used but undocumented: {n} at {first.file}:{first.line}")

print("module 02 ok")
