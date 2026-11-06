# Module 05: Redaction by Construction

## The Concept

There are two ways to keep secrets out of output.

**Redaction by discipline.** Every place that formats output remembers to mask the value. This works until the first
person forgets, and in a tool with six report builders and a dozen error paths someone will.

**Redaction by construction.** The data structures cannot hold a value, so there is nothing to forget.

This module makes the second approach explicit, then adds a safety net for the day a bug defeats it.

## Where Values Could Escape

Follow a secret through the pipeline from modules 01-04:

| Channel | How it leaks | Defence in this codebase |
|---|---|---|
| `repr(entry)` / test failure output | dataclass prints every field | `value` has `repr=False` (module 01) |
| Parse errors | `f"cannot parse {line}"` | errors are `(line number, fixed phrase)` (module 01) |
| A bare secret on its own line | taken as a variable *name* and printed in lists | the parser keeps the line number, drops the word (module 01) |
| Library exceptions | `int("abc")` and `urlsplit` quote the value | validate first; never `str(exception)` (module 04) |
| "Helpful" messages | `f"{name}={value!r} is invalid"` | `check` returns fixed phrases, type words and lengths (module 04) |
| Report objects | any field of type `str` is a candidate | `Finding` has name, line, code, message: no value field |

## The Code

`report_mini.py`:

- `Finding(name, line, code, message)`, frozen. `main.py` asserts these are the only fields; adding `value` would be a
  visible, reviewable change.
- `validate_file` turns parser errors and `check` results into findings. Errors have no name (`""`), only a line.
- `render` prints `line N NAME: code - message`.
- `guard(text, parsed)` is the **trip-wire**. If the value of any secret-looking variable (at least 6 characters)
  appears in the text about to be returned, it raises `RedactionError`, whose own message names the variable and line but
  not the value.

The guard only inspects secret-looking names on purpose. A value like `production` or `3000` matches ordinary words in a
report (file names, "port"), and a guard that cries wolf gets deleted.

The guard is not the defence. It is the alarm for the day the defence has a hole. The tests must prove both: that the
report is clean, and that the guard fires when it is not.

## Run It

```bash
python 05-redaction-by-construction/main.py
```

`main.py` builds a hostile `.env` (a bad port, a bad URL embedding a secret, a garbage line containing a secret, a secret
alone on a line, an unterminated quote) and asserts that the report names the problems by line, contains no secret and
not even the fragment `FAKE`. Then it renders the same entries with a deliberately leaky formatter and confirms
`guard` refuses it.

## What You Learned

- Make the leak impossible in the types, then monitor the boundary anyway.
- A redacted report must still be useful: the test asserts the findings *and* the absence of secrets.
- Safety tests need a sabotage case, or you have not shown the alarm works.
