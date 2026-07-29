# Does "be concise" actually reduce output tokens?

A standalone experiment: does the plain instruction **"Be concise. Keep your
answer short."** make a model generate fewer tokens than saying nothing at all?

**It's unreliable.** On 2 of 5 models it made the model generate *more* — up to
+42% — and on 3 it cut output. A restyling instruction is not a dependable way
to spend fewer tokens.

## Setup

- Two arms, same five final-report tasks:
  - `baseline` — no system prompt.
  - `be_concise` — system prompt `Be concise. Keep your answer short.`
- Metric: **provider output tokens** from the Claude CLI (`usage.output_tokens`),
  summed over 2 runs × 5 tasks per arm.
- Reproduce: `python3 benchmark/be_concise.py`

## Results

| Model | Baseline | "Be concise." | Change | |
|---|---|---|---|---|
| Haiku 4.5 | 3288 | 2666 | −18.9% | fewer |
| Sonnet 5 | 353 | 453 | **+28.3%** | **more** |
| Opus 4.8 | 278 | 394 | **+41.7%** | **more** |
| Fable 5 | 1340 | 1019 | −24.0% | fewer |
| Opus 5 | 591 | 555 | −6.1% | fewer |

## Reading it honestly

- **These numbers stand alone.** This experiment uses 2 runs and a different arm
  set than `bench.py`; its baselines are **not** the same as, and must not be
  compared to, the numbers in the main benchmark tables.
- The finding is about *reliability*, not a universal "concise prompts inflate."
  Telling a model to be concise sometimes trims output and sometimes pads it
  (Sonnet 5 +28%, Opus 4.8 +42%), model-dependently — likely because a terse
  instruction invites a short preamble or restatement on some models while these
  final-answer tasks are already brief.
- NoYap, by contrast, is below baseline on all five models (see the main
  benchmark) because it removes whole sections rather than restyling the prose.
