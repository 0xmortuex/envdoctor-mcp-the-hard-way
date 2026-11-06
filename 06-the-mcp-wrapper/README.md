# Module 06: The MCP Wrapper

## The Concept

The engine from modules 01-05 takes strings and returns strings. Wrapping it in MCP is mostly deciding what an agent
sees and what it is allowed to touch. Three decisions matter.

### 1. A sandbox, enforced where paths are resolved

The server is started with `--dir`, and every tool takes paths relative to it. `resolve()` does the check:

```python
full = os.path.realpath(os.path.join(ROOT, rel))
if os.path.commonpath([ROOT, full]) != ROOT: raise UserError(...)
```

`realpath` resolves symlinks *before* the comparison, so `link.env -> ../outside/secret.env` is caught. Checking the
string `rel` for `..` instead would miss it. The same function is used for every file the server opens, so there is one
place to get it right.

### 2. Errors that are instructions

With `mcp>=2`, a client only sees the message of a `ToolError`; any other exception becomes the unhelpful
"Error executing tool X". So the tool decorator catches `UserError` (an exception *we* raise, with a message we wrote
and know to be safe) and re-raises it as a `ToolError`. Everything unexpected stays hidden: a bug's traceback is not
something to show an agent, and could contain data.

The messages say what to do: `'../x.env' is outside the sandbox folder (the server was started with --dir)`,
`'nope.env' does not exist inside the sandbox folder`. Never `str()` of an arbitrary exception: module 04 showed they can
carry values.

### 3. Tool design

Three tools, each with defaults so the common call is `compare_env()` with no arguments, and docstrings that say what
the tool does, what it never does (show values) and what its arguments mean. The docstring is the only documentation an
agent gets, so it is part of the interface.

`validate_env` wraps its output in `guard(...)` from module 05, the trip-wire on the boundary.

## The Code

`server_mini.py` is about 100 lines: the `tool` decorator, `resolve`, three tools and an `argparse` `main`. It imports the
engine from modules 01-05 through `course.use`. Run it by hand with `python 06-the-mcp-wrapper/server_mini.py --dir
some/project` and point an MCP client at it.

## Run It

```bash
python 06-the-mcp-wrapper/main.py
```

`main.py` launches the server as a real subprocess over stdio, lists the tools, calls all three on the sample project,
makes two calls that must fail (a path outside the sandbox and a missing file), asserts the failures carry the
instructive text, and asserts none of the sample's fake secrets crossed the wire. Finally it checks that `--dir` with a
missing folder exits with status 2 before serving.

## What You Learned

- Resolve paths with `realpath` and compare, in one function that everything uses.
- Convert expected failures to `ToolError` with a safe message; let bugs stay opaque.
- Test the server as a client would: through the transport, not by calling functions.
