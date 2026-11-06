# Break It: The Scanner

## Challenge 1: The Dynamic Read

Add `os.environ[name]` (with `name = "A" + "B"`) to `src/app.py` in `make_sample` and run the scan. What does it report?
What *should* a tool report for a read it cannot resolve?

**Hint:** Nothing. The regex needs a quoted literal. Decide whether silence is acceptable or whether the tool should count
"unresolvable reads" and mention them.

## Challenge 2: The Commented-Out Read

Put `# os.environ["OLD_FLAG"]` into `app.py`. Does `OLD_FLAG` appear as used?

**Hint:** Yes. Making the scanner comment-aware needs a tokenizer per language. Is it worth it? What is the cost of a
false "used" compared with a false "unused"?

## Challenge 3: Follow the Symlink

Change `followlinks=False` to `True`, then make a symlink inside the sample project that points at `/`. What happens?

**Hint:** Loops and escapes. Module 06 returns to the same idea for the sandbox.
