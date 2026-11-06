# Break It: The Tests

## Challenge 1: Mutation by Hand

Edit `report_mini.render` to append `f" [{e.value}]"` somewhere (you will need to pass the entries in). Which tests fail,
and which assertion in each? If none fails, your leak was not reachable from the planted project: extend the fixture.

## Challenge 2: A Test That Cannot Fail

Delete the `test_findings_are_exact` test and make `validate_file` return `[]`. Do the remaining tests pass? What does
that tell you about a suite that only asserts absence?

## Challenge 3: Another Channel

Add a `compare_env` call to the stdio test with a template that has a planted value in `.env.example`. Add a case where
`.env` contains a duplicate of the planted name. Does anything echo it? Where would you look first if it did?
