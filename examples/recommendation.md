# SQLite or PostgreSQL

**Situation:** "Should we use SQLite or PostgreSQL for a multi-user SaaS app with
relational queries, transactions, and expected concurrent writes?"

Verbatim Claude Haiku 4.5 output — no-skill arm vs NoYap arm. Reproduce:
`python3 benchmark/bench.py --mode live --suite final-report` (task `final-05`).

## Without NoYap, 75 tokens

> PostgreSQL.
>
> SQLite is single-writer, so concurrent writes will queue and timeout under load. PostgreSQL handles multi-user concurrency, distributed transactions, and connection pooling—all required for SaaS. SQLite works for prototypes or read-heavy single-tenant apps, but not for this use case.

## With NoYap, 36 tokens

> PostgreSQL.
>
> You need transactions, relational queries, and concurrent writes; SQLite serializes writers — not suitable for multi-user SaaS.

**75 → 36 tokens.** Both answer first — the difference is the second paragraph.
NoYap gives the one reason that decides it (concurrent writers) and stops,
instead of listing every Postgres feature and every SQLite use case you didn't
ask about.
