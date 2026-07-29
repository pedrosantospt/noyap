# Live Claude Benchmark

Live model/API run. Do not compare these numbers to fixture results.

## Metadata

- Provider: `claude-cli`
- Model: `claude-sonnet-5`
- Runs: `3`
- Generated: `2026-07-08T16:07:47.827642+00:00`
- Printed table estimated tokens use `ceil(UTF-8 bytes / 4)`.
- Provider telemetry comes from Claude CLI JSON records when available.
- Simple API cost check uses `$1`/MTok input and `$5`/MTok output.

## Highlights

- Shortest visible output: NoYap (369 estimated visible tokens).
- Lowest provider output tokens: NoYap (592 provider output tokens).
- Lowest provider cost: Ponytail ($0.270279).
- Lowest median latency: Baseline (3707 ms median).

## Comparison

| Skill | Calls | Est output tokens | Est vs baseline | Provider output tokens | Provider vs baseline | Cost USD | Cost vs baseline | Median latency ms | Latency vs baseline | Report overhead |
|---|---|---|---|---|---|---|---|---|---|---|
| Baseline | 15 | 724 | +0.0% | 1134 | +0.0% | 0.334312 | +0.0% | 3707 | +0.0% | 100.0% |
| Caveman | 15 | 618 | +14.6% | 951 | +16.1% | 0.351310 | -5.1% | 4306 | -16.2% | 99.5% |
| Ponytail | 14 | 616 | +14.9% | 886 | +21.9% | 0.270279 | +19.2% | 4157.5 | -12.2% | 100.0% |
| NoYap | 15 | 369 | +49.0% | 592 | +47.8% | 0.274583 | +17.9% | 3773 | -1.8% | 100.0% |

## Provider Telemetry

| Skill | Successful calls | Failures | Provider input tokens | Provider output tokens | Cost USD | Median latency ms |
|---|---|---|---|---|---|---|
| Baseline | 15 | 0 | 43485 | 1134 | 0.334312 | 3707 |
| Caveman | 15 | 0 | 43485 | 951 | 0.351310 | 4306 |
| Ponytail | 14 | 1 | 40586 | 886 | 0.270279 | 4157.5 |
| NoYap | 15 | 0 | 43485 | 592 | 0.274583 | 3773 |

## Cost Sanity Check

| Skill | Provider input tokens | Provider output tokens | Reported cost USD | Simple API cost USD | Reported/simple |
|---|---|---|---|---|---|
| Baseline | 43485 | 1134 | 0.334312 | 0.049155 | 6.80x |
| Caveman | 43485 | 951 | 0.351310 | 0.048240 | 7.28x |
| Ponytail | 40586 | 886 | 0.270279 | 0.045016 | 6.00x |
| NoYap | 43485 | 592 | 0.274583 | 0.046445 | 5.91x |

Reported CLI costs do not match simple input/output token pricing: Baseline 6.80x, Caveman 7.28x, Ponytail 6.00x, NoYap 5.91x. Treat reported cost as Claude CLI telemetry, not raw API token billing.

## Interpretation

- `Est output tokens` measures visible answer size using NoYap's deterministic heuristic.
- `Provider output tokens` and `Cost USD` come from Claude CLI telemetry when present.
- `Simple API cost USD` is input/output token math only.
- Positive delta means lower than baseline; negative delta means higher than baseline.
- NoYap is intended to reduce final-answer waste, not to minimize generated code LOC.

## Warnings

- Ponytail final-05 run 3 failed: API Error: Connection closed mid-response. The response above may be incomplete.

## External Inputs

External comparison skill files were supplied by path at run time and are not vendored into NoYap.
