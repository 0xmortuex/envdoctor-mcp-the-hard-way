# Break It: The Guesser

## Challenge 1: Echo the Exception

In `check`, replace the `bad-port` branch with a `try: int(value) except ValueError as e: return [("bad-port", str(e))]`.
Run `main.py`.

**Hint:** The "no message may contain the value" loop fails. Look at which names and which value it fails for.

## Challenge 2: The Port Nobody Typed

What should `check("PORT", "")` say? What about `PORT=${PORT_DEFAULT}` where the variable is undefined? Compare what the
parser hands you in each case.

**Hint:** An empty value is `empty`, not `bad-port`; the parser already expanded the reference to an empty string. Is that
the right layer to notice an undefined reference?

## Challenge 3: A Secret With a Friendly Name

`SIGNING_PHRASE` and `ENCRYPTION_PASSPHRASE` are secrets. Does `is_secret_name` agree? Extend the regex, then think about
the cost of a false positive (a harmless value flagged) versus a false negative (a secret exposed to the browser).
