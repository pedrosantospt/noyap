# Live Claude Benchmark

Live model/API run. Do not compare these numbers to fixture results.

## Metadata

- Provider: `claude-cli`
- Model: `claude-opus-4-8`
- Runs: `3`
- Generated: `2026-07-08T17:32:20.556920+00:00`
- Printed table estimated tokens use `ceil(UTF-8 bytes / 4)`.
- Provider telemetry comes from Claude CLI JSON records when available.
- Simple API cost check uses `$1`/MTok input and `$5`/MTok output.

## Highlights

- Shortest visible output: Ponytail (536 estimated visible tokens).
- Lowest provider output tokens: NoYap (823 provider output tokens).
- Lowest provider cost: NoYap ($0.408108).
- Lowest median latency: Ponytail (3737 ms median).

## Comparison

| Skill | Calls | Est output tokens | Est vs baseline | Provider output tokens | Provider vs baseline | Cost USD | Cost vs baseline | Median latency ms | Latency vs baseline | Report overhead |
|---|---|---|---|---|---|---|---|---|---|---|
| Baseline | 15 | 656 | +0.0% | 1334 | +0.0% | 0.426001 | +0.0% | 4385 | +0.0% | 100.0% |
| Caveman | 15 | 1063 | -62.0% | 1879 | -40.9% | 0.503244 | -18.1% | 7257 | -65.5% | 98.9% |
| Ponytail | 15 | 536 | +18.3% | 978 | +26.7% | 0.420708 | +1.2% | 3737 | +14.8% | 100.0% |
| NoYap | 15 | 549 | +16.3% | 823 | +38.3% | 0.408108 | +4.2% | 3846 | +12.3% | 100.0% |

## Provider Telemetry

| Skill | Successful calls | Failures | Provider input tokens | Provider output tokens | Cost USD | Median latency ms |
|---|---|---|---|---|---|---|
| Baseline | 15 | 0 | 41610 | 1334 | 0.426001 | 4385 |
| Caveman | 15 | 0 | 41610 | 1879 | 0.503244 | 7257 |
| Ponytail | 15 | 0 | 41610 | 978 | 0.420708 | 3737 |
| NoYap | 15 | 0 | 41610 | 823 | 0.408108 | 3846 |

## Cost Sanity Check

| Skill | Provider input tokens | Provider output tokens | Reported cost USD | Simple API cost USD | Reported/simple |
|---|---|---|---|---|---|
| Baseline | 41610 | 1334 | 0.426001 | 0.048280 | 8.82x |
| Caveman | 41610 | 1879 | 0.503244 | 0.051005 | 9.87x |
| Ponytail | 41610 | 978 | 0.420708 | 0.046500 | 9.05x |
| NoYap | 41610 | 823 | 0.408108 | 0.045725 | 8.93x |

Reported CLI costs do not match simple input/output token pricing: Baseline 8.82x, Caveman 9.87x, Ponytail 9.05x, NoYap 8.93x. Treat reported cost as Claude CLI telemetry, not raw API token billing.

## Interpretation

- `Est output tokens` measures visible answer size using NoYap's deterministic heuristic.
- `Provider output tokens` and `Cost USD` come from Claude CLI telemetry when present.
- `Simple API cost USD` is input/output token math only.
- Positive delta means lower than baseline; negative delta means higher than baseline.
- NoYap is intended to reduce final-answer waste, not to minimize generated code LOC.

## External Inputs

External comparison skill files were supplied by path at run time and are not vendored into NoYap.
