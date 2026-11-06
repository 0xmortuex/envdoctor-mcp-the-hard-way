# Break It: The Parser

## Challenge 1: Forget the Escape

In `find_closing_quote`, delete the `if body[i] == "\\"` branch and run `main.py`. Which snippet fails first, and what
did the parser think the value was?

**Hint:** `"say \"hi\""` now ends at the first inner quote, and `unexpected text after the closing quote` swallows the rest
of the line.

## Challenge 2: Inline Comments Everywhere

Change `INLINE_COMMENT` from `\s+#.*` to `#.*`. Run `main.py`. Then think about `DATABASE_URL=postgres://u:pa#ss@h/db`.

**Hint:** Without the required whitespace, a `#` inside a password silently truncates the value. Real loaders require a
space before the comment marker for exactly this reason.

## Challenge 3: Print an Entry

Add `print(parsed.entries[0])` to `main.py` with a parsed `PASSWORD=hunter2`. Then remove `repr=False` from `Entry.value`
and print it again.

**Hint:** This is how secrets end up in CI logs: a failing `assert entry == ...` prints both sides.
