# Break It: Redaction

## Challenge 1: Add a Field

Add `value: str = ""` to `Finding` and have `validate_file` fill it "for debugging". Run `main.py`. What fails: the
assertion about dataclass fields, the secret check, or both? Why is it good that the first one exists?

## Challenge 2: Partial Leaks

Change `check`'s placeholder message to include the first three characters of the value. Does `guard` catch it? Does the
`"FAKE" not in text` assertion?

**Hint:** The guard compares whole values, so a prefix slips through. The fragment assertion in `main.py` is the second
net. What other fragments could leak (suffix, length-matched mask, hash)? Which are acceptable?

## Challenge 3: The Guard Is Too Clever

Make `guard` check every value of at least 3 characters, not only secret-looking names. Run `main.py` of this module and of module 07.

**Hint:** Values like `eu-west-1` appear in ordinary text. A guard with false alarms teaches people to bypass it.
