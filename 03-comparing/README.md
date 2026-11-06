# Module 03: Comparing

## The Concept

The question a new teammate asks first is "what do I have to put in my `.env`?". The answer is a diff between two
files, with a twist: the useful diff compares *names*, and the values must never be part of it.

`compare(real, template)` returns four lists:

| List | Meaning | Why it matters |
|---|---|---|
| `missing` | in the template, absent from `.env` | the app will start with a hole in its config |
| `extra` | in `.env`, unknown to the template | undocumented config, or a typo (`DATABSE_URL`) |
| `empty` | listed by the template, present in `.env` with no value | `KEY=` overrides a default with an empty string |
| `duplicated` | defined more than once, with line numbers | the earlier ones are silently ignored |

## The Code

`compare_mini.py` is small because module 01 did the hard part. The things to notice:

- `Parsed.last()` already collapses duplicates (the last one wins), so `missing` and `extra` are plain dict-key
  comparisons.
- Duplicates are computed from *entries*, not from the dict, because the dict has already forgotten them.
- `render` prints names, counts and line numbers. Look at it again after module 05: the output is safe not because
  someone remembered to redact, but because the `Comparison` never held a value in the first place.

The full server adds three refinements you can try as exercises: a `# optional` comment above a template line exempts it
from "missing/empty", commented-out template lines (`# FLAG=`) count as documented, and values whose *type* differs from
the template's (template `PORT=3000`, real `PORT=abc`) are flagged using module 04's type guesser.

## Run It

```bash
python 03-comparing/main.py
```

The sample project's `.env` differs from its template in four ways, and `main.py` asserts the exact rendered report.

## What You Learned

- Compare names, not values.
- Keep the information you need later (duplicate lines) before a convenient structure throws it away.
- A result object made only of names and numbers cannot leak.
