# Examples

Real model output — the same prompt answered **without any skill**
(`## Without NoYap`) and **with NoYap** (`## With NoYap`, i.e.
`skills/noyap/SKILL.md` loaded as the system prompt), so you can compare side by
side. Model: **Claude Haiku 4.5**. Token counts are `ceil(UTF-8 bytes / 4)` of
the full response; the two code-heavy answers have blank lines trimmed for
display, the rest are verbatim.

These are not hand-written. The report/decision/status cases come straight from
the benchmark (`python3 benchmark/bench.py --mode live --suite final-report`);
the how-to/debug cases are the listed prompt run with and without the skill.
Method and the four-model numbers: [`../benchmark/`](../benchmark/).

| Example | What it shows | Without | With | Cut |
|---|---|--:|--:|--:|
| [Migration risk](migration-risk.md) | Risk gate — names the one real risk, invents nothing | 158 tok | 35 tok | **4.5×** |
| [Unverified patch](unverified-patch.md) | Proof gate — says `Not run.` instead of faking done | 41 tok | 13 tok | **3.2×** |
| [SQLite or Postgres](recommendation.md) | Answer first, one reason | 75 tok | 36 tok | **2.1×** |
| [HTTP timeout](http-timeout.md) | Answers the question, skips the kitchen sink | 314 tok | 170 tok | **1.8×** |
| [Blocked on a bug](blocked.md) | Asks once for the minimum missing info | 67 tok | 42 tok | **1.6×** |
| [Slow Postgres query](slow-query.md) | Answer-first debugging, no bloat | 300 tok | 201 tok | **1.5×** |

**Honest note.** NoYap's edge is largest on report, decision, and status tasks,
where a plain agent pads or fakes confidence. On a genuine "explain this" or
"how do I" question it gives the full answer — it trims ceremony, not substance.
It doesn't pad, and it doesn't over-cut.
