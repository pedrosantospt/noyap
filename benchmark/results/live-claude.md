# Live Claude Benchmark

Live model/API run. Do not compare these numbers to fixture results.

## Metadata

- Provider: `claude-cli`
- Model: `claude-haiku-4-5-20251001`
- Runs: `3`
- Generated: `2026-07-08T14:56:19.717594+00:00`
- Printed table estimated tokens use `ceil(UTF-8 bytes / 4)`.
- Provider telemetry comes from Claude CLI JSON records when available.
- Simple API cost check uses `$1`/MTok input and `$5`/MTok output.

## Highlights

- Shortest visible output: NoYap (479 estimated visible tokens).
- Lowest provider output tokens: NoYap (4152 provider output tokens).
- Lowest provider cost: NoYap ($0.087554).
- Lowest median latency: Baseline (6305 ms median).

## Comparison

| Skill | Calls | Est output tokens | Est vs baseline | Provider output tokens | Provider vs baseline | Cost USD | Cost vs baseline | Median latency ms | Latency vs baseline | Report overhead |
|---|---|---|---|---|---|---|---|---|---|---|
| Baseline | 15 | 1159 | +0.0% | 4732 | +0.0% | 0.102870 | +0.0% | 6305 | +0.0% | 100.0% |
| Caveman | 15 | 1137 | +1.9% | 5219 | -10.3% | 0.110227 | -7.2% | 6845 | -8.6% | 99.4% |
| Ponytail | 15 | 1194 | -3.0% | 5554 | -17.4% | 0.095163 | +7.5% | 7569 | -20.0% | 100.0% |
| NoYap | 15 | 479 | +58.7% | 4152 | +12.3% | 0.087554 | +14.9% | 6561 | -4.1% | 100.0% |

## Provider Telemetry

| Skill | Successful calls | Failures | Provider input tokens | Provider output tokens | Cost USD | Median latency ms |
|---|---|---|---|---|---|---|
| Baseline | 15 | 0 | 135 | 4732 | 0.102870 | 6305 |
| Caveman | 15 | 0 | 150 | 5219 | 0.110227 | 6845 |
| Ponytail | 15 | 0 | 135 | 5554 | 0.095163 | 7569 |
| NoYap | 15 | 0 | 135 | 4152 | 0.087554 | 6561 |

## Cost Sanity Check

| Skill | Provider input tokens | Provider output tokens | Reported cost USD | Simple API cost USD | Reported/simple |
|---|---|---|---|---|---|
| Baseline | 135 | 4732 | 0.102870 | 0.023795 | 4.32x |
| Caveman | 150 | 5219 | 0.110227 | 0.026245 | 4.20x |
| Ponytail | 135 | 5554 | 0.095163 | 0.027905 | 3.41x |
| NoYap | 135 | 4152 | 0.087554 | 0.020895 | 4.19x |

Reported CLI costs do not match simple input/output token pricing: Baseline 4.32x, Caveman 4.20x, Ponytail 3.41x, NoYap 4.19x. Treat reported cost as Claude CLI telemetry, not raw API token billing.

## Interpretation

- `Est output tokens` measures visible answer size using NoYap's deterministic heuristic.
- `Provider output tokens` and `Cost USD` come from Claude CLI telemetry when present.
- `Simple API cost USD` is input/output token math only.
- Positive delta means lower than baseline; negative delta means higher than baseline.
- NoYap is intended to reduce final-answer waste, not to minimize generated code LOC.

## External Inputs

External comparison skill files were supplied by path at run time and are not vendored into NoYap.
