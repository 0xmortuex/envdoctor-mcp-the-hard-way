# Break It: The Comparison

## Challenge 1: Case

Rename `PORT` to `port` in `.env`. What does `compare` say? What would a developer on macOS vs Linux vs Windows
experience when the app reads `PORT`?

**Hint:** Names are case-sensitive in POSIX and case-insensitive on Windows. Decide what a diagnostic should do, and
whether it should say so.

## Challenge 2: Optional Variables

Implement the `# optional` rule: a comment line containing "optional" directly above a template line exempts it from
`missing` and `empty`. Where must the information be captured: in the comparer or in the parser?

**Hint:** The parser sees comments; the comparer does not. Add a field to `Entry`.

## Challenge 3: Leak on Purpose

Change `render` to print `f"{name}={entry.value}"` for `empty` entries "to make it clearer". Run module 05's `main.py`
afterwards.

**Hint:** Not in this module's tests, which is exactly the point of module 05: you need a test that fails on a leak.
