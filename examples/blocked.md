# Blocked on a bug

**Situation:** A user reports a production bug but gives no stack trace, logs,
reproduction steps, or affected version. Write the response asking for the
minimum you need.

Verbatim Claude Haiku 4.5 output — no-skill arm vs NoYap arm. Reproduce:
`python3 benchmark/bench.py --mode live --suite final-report` (task `final-03`).

## Without NoYap, 67 tokens

> To investigate this bug, I need:
>
> 1. **Stack trace** — the full error output
> 2. **Steps to reproduce** — exactly what triggers the issue
> 3. **Affected version** — which release/commit this impacts
>
> One of these three will unblock me. Which can you provide first?

## With NoYap, 42 tokens

> Blocked: insufficient information to investigate.
>
> Provide: (1) stack trace or error message, (2) affected version, (3) how to reproduce (or last successful version).

**67 → 42 tokens.** Both ask for the same three things. NoYap states the blocked
status up front and asks once, in one line, instead of formatting the request as
a numbered explainer and closing with a follow-up question.
