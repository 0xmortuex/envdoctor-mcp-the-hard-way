# Module 04: Type Guessing

## The Concept

The most common `.env` bug is a value of the wrong *kind*: `PORT=3000x`, `DEBUG=maybe`, `API_URL=localhost:3000` (no
scheme), a placeholder nobody replaced. Spotting them needs two sources of evidence:

1. **What the name promises.** `*_PORT` should be a port, `*_URL` a URL, `ENABLE_*` a boolean.
2. **What the value looks like.** `guess_type` returns `empty`, `bool`, `int`, `url`, `dsn`, `email`, `jwt` or `string`.

A disagreement between the two is a finding. Names are convention, so these are hints, not rules, and the messages say
"name says port but the value looks like string" rather than "invalid".

## The Code

`shapes_mini.py`:

- `expected_type(name)`: suffix and prefix conventions.
- `guess_type(value)`: ordered tests (empty, bool, int, URL/DSN by scheme, JWT, email). `1` and `0` are ints, not
  bools: the *name* (`DEBUG`, `ENABLE_X`) decides when they are acceptable booleans.
- `is_placeholder(value)`: `changeme`, `your_api_key_here`, `<token>`, `xxxx`, `TODO`.
- `check(name, value)`: returns `(code, fixed message)` pairs.
- Client exposure: `VITE_`, `NEXT_PUBLIC_` and `REACT_APP_` variables are compiled into the browser bundle. If such a name
  also looks secret (`TOKEN`, `SECRET`, `PASSWORD`...), it is shipped to every visitor.

## The Trap: Exception Messages Contain the Value

Look at the `bad-port` and `bad-url` branches. This code is tempting:

```python
try:
    int(value)
except ValueError as e:
    return [("bad-port", str(e))]   # "invalid literal for int() with base 10: 'abc'"
```

The exception text embeds the value. `urlsplit("http://h:abc").port` raises "Port could not be cast to integer value as
'abc'". So `check` validates with a regex *before* calling `int`, and treats a `ValueError` from `urlsplit` as a boolean,
never as text. The test in `main.py` feeds a secret through every branch, including the one that makes `urlsplit` raise,
and asserts it appears in no message.

The rule: **messages are fixed phrases plus type words and lengths. Never `str(exception)`, never a slice of the value.**

## Run It

```bash
python 04-type-guessing/main.py
```

## What You Learned

- Combine name evidence and value evidence; report disagreement as a hint.
- Library exceptions are a hidden channel for the data you are trying to protect.
- Describe values (type, length), do not quote them.
