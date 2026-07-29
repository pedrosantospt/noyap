# Live Claude Benchmark

Live model/API run. Do not compare these numbers to fixture results.

## Metadata

- Provider: `claude-cli`
- Model: `claude-fable-5`
- Runs: `3`
- Generated: `2026-07-08T22:00:44.819224+00:00`
- Printed table estimated tokens use `ceil(UTF-8 bytes / 4)`.
- Provider telemetry comes from Claude CLI JSON records when available.
- Simple API cost check uses `$1`/MTok input and `$5`/MTok output.

## Highlights

- Shortest visible output: NoYap (516 estimated visible tokens).
- Lowest provider output tokens: NoYap (1229 provider output tokens).
- Lowest provider cost: NoYap ($0.845886).
- Lowest median latency: NoYap (6736 ms median).

## Comparison

| Skill | Calls | Est output tokens | Est vs baseline | Provider output tokens | Provider vs baseline | Cost USD | Cost vs baseline | Median latency ms | Latency vs baseline | Report overhead |
|---|---|---|---|---|---|---|---|---|---|---|
| Baseline | 15 | 1169 | +0.0% | 2933 | +0.0% | 1.075560 | +0.0% | 7696 | +0.0% | 100.0% |
| Caveman | 15 | 839 | +28.2% | 2622 | +10.6% | 1.051766 | +2.2% | 8447 | -9.8% | 98.9% |
| Ponytail | 15 | 903 | +22.8% | 2277 | +22.4% | 0.914486 | +15.0% | 8426 | -9.5% | 100.0% |
| NoYap | 15 | 516 | +55.9% | 1229 | +58.1% | 0.845886 | +21.4% | 6736 | +12.5% | 100.0% |

## Provider Telemetry

| Skill | Successful calls | Failures | Provider input tokens | Provider output tokens | Cost USD | Median latency ms |
|---|---|---|---|---|---|---|
| Baseline | 15 | 0 | 41611 | 2933 | 1.075560 | 7696 |
| Caveman | 15 | 0 | 41610 | 2622 | 1.051766 | 8447 |
| Ponytail | 15 | 0 | 41610 | 2277 | 0.914486 | 8426 |
| NoYap | 15 | 0 | 41610 | 1229 | 0.845886 | 6736 |

## Cost Sanity Check

| Skill | Provider input tokens | Provider output tokens | Reported cost USD | Simple API cost USD | Reported/simple |
|---|---|---|---|---|---|
| Baseline | 41611 | 2933 | 1.075560 | 0.056276 | 19.11x |
| Caveman | 41610 | 2622 | 1.051766 | 0.054720 | 19.22x |
| Ponytail | 41610 | 2277 | 0.914486 | 0.052995 | 17.26x |
| NoYap | 41610 | 1229 | 0.845886 | 0.047755 | 17.71x |

Reported CLI costs do not match simple input/output token pricing: Baseline 19.11x, Caveman 19.22x, Ponytail 17.26x, NoYap 17.71x. Treat reported cost as Claude CLI telemetry, not raw API token billing.

## Interpretation

- `Est output tokens` measures visible answer size using NoYap's deterministic heuristic.
- `Provider output tokens` and `Cost USD` come from Claude CLI telemetry when present.
- `Simple API cost USD` is input/output token math only.
- Positive delta means lower than baseline; negative delta means higher than baseline.
- NoYap is intended to reduce final-answer waste, not to minimize generated code LOC.

## External Inputs

External comparison skill files were supplied by path at run time and are not vendored into NoYap.
