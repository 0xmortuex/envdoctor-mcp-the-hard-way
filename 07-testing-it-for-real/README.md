# Module 07: Testing It For Real

## The Concept

For most servers, "it works" means "it returns the right answer". For this one the property that matters is negative:
**no value ever appears.** Negative properties are easy to claim and hard to verify, because a test that finds nothing
could be broken. Four techniques make the evidence real.

### 1. Plant unique, fake values

`test_mini.py` writes a project whose secrets are `PLANTED-alpha-0001-zzz` and friends. They are unique, so a plain
substring search over the output is a sound leak detector. No regex, no entropy guessing.

### 2. Make the project hostile

The `.env` is not tidy. It contains a bad port and a bad URL *with a planted secret in them* (the shape errors a lazy
implementation would quote), a garbage line, a secret alone on a line, and an unterminated quote that swallows the rest of
the file. Every channel that could echo a value gets used.

### 3. Assert the findings too

`test_findings_are_exact` pins the full list of `(line, name, code)`. Without it, a "fix" that makes the tool say nothing
would pass the leak test. Redaction must not be achieved by silence.

### 4. Sabotage the thing under test

`test_guard_catches_a_leaky_formatter` builds the leak a hurried developer would write (`f"{name}={value}"`) and demands
that `guard` refuses it, and that the refusal itself does not contain the value. A safety net you have never seen catch
anything is a hope.

## Real Systems, Not Mocks

The stdio test launches `server_mini.py` as a subprocess and talks to it with the real MCP client, so it covers argument
parsing, the sandbox, the `ToolError` conversion and the transport. The symlink test creates a real symlink (and skips
itself with a stated reason if the OS forbids it, as Windows can without Developer Mode). Nothing is mocked, and nothing
depends on the machine: the projects live in `tmp_path`, paths are never hard-coded, and fixture files are written as
bytes so newline translation cannot change them.

## The Full Server

The real [envdoctor-mcp](https://github.com/0xmortuex/envdoctor-mcp) applies the same ideas at scale: temp projects in
several languages with exact assertions, a hostile project run through all six tools, a stdio transcript checked for
planted values, a cross-check of its parser against python-dotenv, and real git repositories for the gitignore tool.

## Run It

```bash
python 07-testing-it-for-real/main.py
# or directly:
python -m pytest 07-testing-it-for-real/test_mini.py -q
```

## What You Learned

- Prove a negative with unique planted values, a hostile input and a sabotage case.
- Pair every "does not leak" assertion with a "still reports the problem" assertion.
- Test through the transport, with real files and processes.
