# Contributing

Keep it small. Keep it honest.

## Rules

- Do not fabricate benchmark results.
- Do not claim tests or live runs unless they happened.
- Keep core NoYap behavior independent: no external baseline names in the skill or adapters.
- External baseline names belong only in results contexts: `research/`, `benchmark/`, and the README benchmark table.
- Prefer stdlib Python for benchmark code.
- Add dependencies only when there is no boring alternative.
- Keep examples compact and realistic.

## Local Checks

```bash
make check
```

If your system only has a project venv, use that interpreter instead.

## Pull Requests

Include:

- What changed.
- What was run.
- Any benchmark/provenance impact.
- Any known limitation.

By participating, you agree to `CODE_OF_CONDUCT.md`.
