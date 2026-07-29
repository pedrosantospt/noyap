# Live Claude Benchmark

Live model/API run. Do not compare these numbers to fixture results.

## Metadata

- Provider: `claude-cli`
- Model: `claude-opus-5`
- Runs: `3`
- Generated: `2026-07-29T18:20:48.215274+00:00`
- Printed table estimated tokens use `ceil(UTF-8 bytes / 4)`.
- Provider telemetry comes from Claude CLI JSON records when available.
- Simple API cost check uses `$1`/MTok input and `$5`/MTok output.

## Highlights

- Shortest visible output: NoYap (489 estimated visible tokens).
- Lowest provider output tokens: NoYap (745 provider output tokens).
- Lowest provider cost: NoYap ($0.375845).
- Lowest median latency: Baseline (3867 ms median).

## Comparison

| Skill | Calls | Est output tokens | Est vs baseline | Provider output tokens | Provider vs baseline | Cost USD | Cost vs baseline | Median latency ms | Latency vs baseline | Report overhead |
|---|---|---|---|---|---|---|---|---|---|---|
| Baseline | 15 | 660 | +0.0% | 1078 | +0.0% | 0.383370 | +0.0% | 3867 | +0.0% | 100.0% |
| Caveman | 15 | 620 | +6.1% | 951 | +11.8% | 0.447389 | -16.7% | 4273 | -10.5% | 100.0% |
| Ponytail | 15 | 683 | -3.5% | 992 | +8.0% | 0.388884 | -1.4% | 4033 | -4.3% | 100.0% |
| NoYap | 15 | 489 | +25.9% | 745 | +30.9% | 0.375845 | +2.0% | 3886 | -0.5% | 100.0% |

## Provider Telemetry

| Skill | Successful calls | Failures | Provider input tokens | Provider output tokens | Cost USD | Median latency ms |
|---|---|---|---|---|---|---|
| Baseline | 15 | 0 | 30 | 1078 | 0.383370 | 3867 |
| Caveman | 15 | 0 | 30 | 951 | 0.447389 | 4273 |
| Ponytail | 15 | 0 | 30 | 992 | 0.388884 | 4033 |
| NoYap | 15 | 0 | 30 | 745 | 0.375845 | 3886 |

## Cost Sanity Check

| Skill | Provider input tokens | Provider output tokens | Reported cost USD | Simple API cost USD | Reported/simple |
|---|---|---|---|---|---|
| Baseline | 30 | 1078 | 0.383370 | 0.005420 | 70.73x |
| Caveman | 30 | 951 | 0.447389 | 0.004785 | 93.50x |
| Ponytail | 30 | 992 | 0.388884 | 0.004990 | 77.93x |
| NoYap | 30 | 745 | 0.375845 | 0.003755 | 100.09x |

Reported CLI costs do not match simple input/output token pricing: Baseline 70.73x, Caveman 93.50x, Ponytail 77.93x, NoYap 100.09x. Treat reported cost as Claude CLI telemetry, not raw API token billing.

## Interpretation

- `Est output tokens` measures visible answer size using NoYap's deterministic heuristic.
- `Provider output tokens` and `Cost USD` come from Claude CLI telemetry when present.
- `Simple API cost USD` is input/output token math only.
- Positive delta means lower than baseline; negative delta means higher than baseline.
- NoYap is intended to reduce final-answer waste, not to minimize generated code LOC.

## External Inputs

External comparison skill files were supplied by path at run time and are not vendored into NoYap.
