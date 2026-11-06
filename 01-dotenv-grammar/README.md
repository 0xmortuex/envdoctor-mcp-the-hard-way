# Module 01: The dotenv Grammar

## The Concept

"A `.env` file is `KEY=value` per line" is true for the first ten minutes of a project. Then someone writes:

```
export REGION=eu-west-1          # where we run
GREETING="hello ${REGION}"
MOTD='it\'s fine'
CERT="-----BEGIN CERT-----
line two
-----END CERT-----"
PORT=3000
PORT=3001
```

and every tool that reads the file has an opinion. A diagnostic tool has to agree with the loader your app actually
uses, otherwise it reports problems that are not there and misses the ones that are. So the first job is to write the
parser, and to measure it against the reference instead of trusting your memory of the rules.

## The Rules (python-dotenv's)

| Situation | Behaviour |
|---|---|
| blank line, `# comment` | skipped |
| `export KEY=v` | `export ` ignored |
| `KEY = v` | spaces around `=` allowed |
| `KEY=hello world` | unquoted: value is `hello world` |
| `KEY=v   # note` | unquoted: an inline comment starts at whitespace + `#` |
| `KEY=v#x` | no whitespace before `#`, so it is part of the value |
| `'...'` | single quotes: literal, except `\'` and `\\` |
| `"..."` | double quotes: escapes (`\n`, `\t`, `\"`, `\\`...) and may span lines |
| `${VAR}`, `${VAR:-d}` | expanded against earlier variables in the same file |
| `KEY=1` twice | both exist, the last one wins |

## The Code

`dotenv_mini.py` is one function, `parse`, plus three helpers. Three design decisions matter later.

**`Entry.value` has `repr=False`.** A dataclass prints every field by default, so a stray `print(entry)` or a pytest
assertion failure would put the secret in a log. Hiding it from `repr` costs one argument.

**Errors are `(line number, fixed phrase)`.** The tempting message is `f"cannot parse {line!r}"`. That puts the offending
text, which may be a secret, into the error. Module 05 builds on this.

**A bare word on a line is an error, not a variable.** python-dotenv would read `KEY` alone as a variable with no value.
But a line that holds a single word might be a token somebody pasted on its own line. If the parser turned it into a
variable *name*, every later report would print it. So the parser keeps the line number and drops the word.

Expansion uses only variables defined earlier in the same file, never `os.environ`. The result must not depend on the
machine the diagnosis runs on.

## Run It

```bash
python 01-dotenv-grammar/main.py
```

`main.py` parses 17 snippets and asserts that every value matches `dotenv_values()` from python-dotenv, then checks
expansion, duplicates, the fixed-phrase errors and the hidden `repr`.

## What You Learned

- The grammar is small but has real corners: quoting decides escapes, comments and expansion.
- Verifying against the reference loader beats reasoning from memory.
- Two redaction rules already live in the parser: no value in `repr`, no text in errors.
