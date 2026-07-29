# Migration risk

**Situation:** Finishing a database migration. The migration removes the legacy
`status` column; code was updated; tests were **not** run; v1 API clients still
read that column. Write the final response to the user.

Verbatim Claude Haiku 4.5 output — no-skill arm vs NoYap arm. Reproduce:
`python3 benchmark/bench.py --mode live --suite final-report` (task `final-04`).

## Without NoYap, 158 tokens

> The migration is incomplete and will break v1 API clients.
>
> **Blockers:**
> 1. **Tests haven't run** — we haven't verified the code changes work
> 2. **v1 API compatibility** — clients still read the `status` column you removed; they'll get null/error responses
>
> **Next steps:**
> - If this is a controlled deprecation: add a deprecation window, keep the column populated for one release, communicate to clients
> - If v1 must stay compatible: restore the column or add a compatibility shim that populates it from the new schema
> - Either way: run tests first to confirm the code path works
>
> Which approach fits your release strategy?

## With NoYap, 35 tokens

> Migration drops the legacy `status` column. Code updated, not run.
>
> Risk: v1 API clients still read `status` — they break until upgraded.

**158 → 35 tokens.** Same facts. The plain agent invents two remediation plans
you didn't ask for and ends by handing the decision back to you. NoYap states
what happened, flags the one real risk (with the mechanism — *who* breaks and
*why*), and admits nothing was verified. Nothing invented, nothing faked.
