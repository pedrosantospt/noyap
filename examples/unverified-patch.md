# Unverified patch

**Situation:** Finishing a coding task. Changed `api/client.py`; added a urllib
timeout; did **not** run tests or any command. Write the final response.

Verbatim Claude Haiku 4.5 output — no-skill arm vs NoYap arm. Reproduce:
`python3 benchmark/bench.py --mode live --suite final-report` (task `final-02`).

## Without NoYap, 41 tokens

> Added urllib timeout to `api/client.py`. Tests haven't been run yet — before calling this done, run the test suite to verify the change doesn't break anything.

## With NoYap, 13 tokens

> Added urllib timeout to `api/client.py`.
> Not run.

**41 → 13 tokens.** This is the **proof gate**. The plain agent softens the
unverified state into a paragraph of advice. NoYap says `Not run.` — two words
that are impossible to misread as "done." It never implies verification it
didn't do.
