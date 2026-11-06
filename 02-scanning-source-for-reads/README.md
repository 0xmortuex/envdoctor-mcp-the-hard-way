# Module 02: Scanning Source for Reads

## The Concept

A `.env.example` is a promise about what the code needs. Code and promise drift apart in two directions:

- the code reads `SENTRY_DSN`, nobody documented it, and the next developer's app boots with Sentry silently off
- the template still lists `UNUSED_VAR` from a feature deleted a year ago

To find both you have to read the code. Without a parser for every language, the pragmatic tool is a table of regexes,
one family per language, where group 1 is always the variable name:

| Language | Reads recognised |
|---|---|
| JS / TS / Vue | `process.env.X`, `process.env["X"]`, `import.meta.env.X`, `const { X, Y } = process.env` |
| Python | `os.environ["X"]`, `os.environ.get("X")`, `os.getenv("X")` |
| Ruby | `ENV["X"]`, `ENV.fetch("X")` |
| Rust | `std::env::var("X")`, `env::var_os("X")` |
| Go | `os.Getenv("X")`, `os.LookupEnv("X")` |
| Java / Kotlin | `System.getenv("X")` |

(The full server adds C#, PHP, Elixir, Prisma, `${X}` in compose files and more. The idea is identical.)

## The Code

`scan_mini.py` has three layers.

**`scan_text(text, lang, rel)`** applies a language's regexes to one file and returns `Usage(name, file, line)`. Line
numbers come from a list of line-start offsets and `bisect`, so a match anywhere in a multi-line file is located in
O(log n) without splitting the text.

**`DESTRUCTURE`** handles `const { A, B: renamed = 1, ...rest } = process.env`. No `process.env.A` ever appears, yet
`A` is read. It splits the braces on commas and takes the leading identifier of each part, skipping `...rest`.

**`scan_tree(root)`** walks the project, prunes `node_modules`, `.git`, virtualenvs and build output (`followlinks=False`:
a symlink out of the tree must not drag the scan along), and dispatches on the file extension.

`cross_check(used, documented)` is two set differences. Two filters keep it honest: `VITE_BUILTINS` (Vite always
provides `MODE`, `DEV`...) and `AMBIENT` (`PATH`, `HOME`, `NODE_ENV`... every process has them, so listing them as
"undocumented" is noise).

## What It Cannot Do

Say this to the agent, not just in a README:

- It is a text scan. A match inside a comment counts.
- `process.env[name]` with a dynamic name is invisible.
- "Documented but unused" can be wrong: frameworks, shell scripts and Dockerfiles also read variables.

A diagnostic that overclaims gets ignored the first time it is wrong. The real server's tool descriptions state these
limits up front.

## Run It

```bash
python 02-scanning-source-for-reads/main.py
```

`main.py` asserts exact `(name, line)` results for a snippet in each language, then scans the sample project and checks
that `SENTRY_DSN`, `VITE_API_URL` and `VITE_STRIPE_SECRET_KEY` are used but undocumented.

## What You Learned

- A table of regexes plus a good fixture gets most of the value for a fraction of the effort.
- Locate matches by offset, not by splitting.
- Know and state what a heuristic cannot see.
