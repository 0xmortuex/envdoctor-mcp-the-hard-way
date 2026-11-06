# Break It: The Wrapper

## Challenge 1: Print to Stdout

Add `print("reading", rel)` to `read_env` and run `main.py`.

**Hint:** In stdio mode stdout *is* the protocol. A stray line is not valid JSON-RPC and the client may error or
desynchronise. Logs go to stderr.

## Challenge 2: A Naive Sandbox

Replace `resolve` with `if ".." in rel: raise UserError(...)` and keep the rest. Which of module 07's tests fails?

**Hint:** The symlink test. A link inside the sandbox can point anywhere; only `realpath` sees where it really goes.

## Challenge 3: Let the Exception Through

Remove the `except UserError` in `tool` so errors propagate. What does the client see for an out-of-sandbox path?

**Hint:** A generic "Error executing tool validate_env", with nothing to act on. Compare it with the message in
`main.py`'s assertion.
