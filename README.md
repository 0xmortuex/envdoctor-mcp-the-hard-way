# envdoctor-mcp — The Hard Way

Build an MCP server that diagnoses a project's environment variables **without ever showing a value**. You write the
dotenv parser, the source scanner, the comparer, the type guesser and the MCP wrapper yourself, and you test the one
property that matters: a planted fake secret never appears in any output.

At the end you will have built a small version of [envdoctor-mcp](https://github.com/0xmortuex/envdoctor-mcp), and you
will understand the part most MCP tutorials skip: **how to design a server whose safety is a property of its data
structures, and how to prove it with tests.**

## Why This Exists

Most MCP tutorials wrap a REST API. This one wraps a problem where the obvious implementation is dangerous. Anything that
helps debug a `.env` file is tempted to print the value ("PORT is `abc`, expected a number"), and an agent's tool output
goes into a model's context, into logs, into transcripts. The interesting engineering questions are:

- how a dotenv file is really parsed (quotes, escapes, `export`, comments, multiline values, `${VAR}`)
- finding environment reads in source code across languages with nothing but regexes, and being honest about the limits
- reporting useful diagnostics from *shapes* (names, lengths, type guesses) instead of values
- making a leak structurally impossible, then adding a trip-wire for the day you are wrong
- failing in ways that tell the agent what to do next

## Who This Is For

- developers who have built a "hello world" MCP server and want to build a real one
- anyone who has pasted a `.env` into a chat and then felt uneasy about it

**Prerequisites:** Python 3.10+ and `pip install -r requirements.txt` (the `mcp` SDK, pytest, and python-dotenv, which
module 01 uses to check your parser against the reference). Nothing else: no network, no external binaries.

## Modules

| # | Module | What You'll Build |
|---|--------|-------------------|
| 01 | [The dotenv Grammar](01-dotenv-grammar/) | A parser for quotes, escapes, `export`, inline comments, multiline values, `${VAR}` expansion and duplicates, checked against python-dotenv |
| 02 | [Scanning Source for Reads](02-scanning-source-for-reads/) | Regexes for `process.env`, `import.meta.env`, `os.environ`, `ENV[]`, `env::var`, `os.Getenv`, `System.getenv`, with file:line, and the used-vs-documented cross-check |
| 03 | [Comparing](03-comparing/) | `.env` vs `.env.example`: missing, extra, empty-but-required, duplicated |
| 04 | [Type Guessing](04-type-guessing/) | Guessing URL/port/bool/DSN/JWT/email from names and values, placeholders, browser-exposed secrets, and the exception messages that leak |
| 05 | [Redaction by Construction](05-redaction-by-construction/) | A `Finding` type with nowhere to put a value, fixed-phrase errors, and a guard that trips if a secret ever reaches the output |
| 06 | [The MCP Wrapper](06-the-mcp-wrapper/) | An MCP server with a `--dir` sandbox, symlink-proof path resolution and errors an agent can act on |
| 07 | [Testing It For Real](07-testing-it-for-real/) | Planted secrets in hostile files, a real stdio session, a deliberately leaky formatter the guard must catch |

Each module contains a `README.md` (the why), a code file (the what), a `main.py` that **checks its own results with
`assert`** and a `break-it.md` with experiments.

## Running It

```bash
pip install -r requirements.txt
python verify.py          # runs every module's main.py; each must exit 0
python verify.py 05       # just one module
python 03-comparing/main.py
```

`verify.py` runs on Linux and Windows in CI (`.github/workflows/verify.yml`). Each module adds one file and imports the
earlier ones through `course.use(...)`, so you can read them in order like a book.

All "secrets" in this repository are obviously fake strings created by `course.make_sample`; no real credential is
involved anywhere.

MIT licensed.
