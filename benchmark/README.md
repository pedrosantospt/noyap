# Benchmark

Fixture benchmark. Not live model/API usage.

## Do I Need Claude Code?

No for fixture mode.

Fixture mode only needs Python 3.11+ and stdlib. It reads saved fixture outputs and measures them deterministically.

You need Claude Code for live mode. Live mode runs `claude -p` and requires authenticated Claude Code plus external paths to the comparison skill files.

## Modes

- `fixture`: loads saved outputs from `benchmark/fixtures/`.
- `live`: runs the same tasks through `claude -p` for Baseline, Caveman, Ponytail, and NoYap.

## Metrics

- Estimated tokens: `ceil(len(text.encode("utf-8")) / 4)`.
- Code blocks: triple backticks with optional language tags.
- LOC: non-empty lines inside fenced code blocks.
- Code tokens: estimated tokens inside fenced code blocks.
- Report tokens: estimated tokens outside fenced code blocks.
- Report overhead: `report_tokens / total_output_tokens`.

Estimated tokens are deterministic approximations, not provider-reported usage.

## Commands

```bash
python3 benchmark/bench.py
python3 benchmark/bench.py --format markdown
python3 benchmark/bench.py --csv benchmark/results/summary.csv
python3 benchmark/bench.py --json benchmark/results/summary.json
```

The comparison rows are stable: Caveman, Ponytail, NoYap. External baseline fixtures are synthetic examples unless provenance says otherwise.

## Live Claude Code Mode

Live mode is intentionally explicit:

- requires `claude` on `PATH`
- requires authenticated Claude Code
- requires external paths to the comparison skill files
- stores raw per-run records in JSON when `--json` is supplied
- never downloads or vendors external skill files

Check auth first:

```bash
claude -p --output-format json "Say OK"
```

If it returns `Not logged in`, open an interactive Claude Code session and run `/login`, or use your installed CLI's auth flow (`claude auth` on recent versions).

Fetch pinned external sources first:

```bash
python3 benchmark/fetch_baselines.py
```

This clones the inspected upstream repositories into `benchmark/external/`, checks out pinned commits, and prints the exact live benchmark command.

Example:

```bash
python3 benchmark/bench.py \
  --mode live \
  --suite coding \
  --provider claude-cli \
  --runs 3 \
  --model claude-haiku-4-5-20251001 \
  --caveman-skill benchmark/external/caveman/skills/caveman/SKILL.md \
  --ponytail-skill benchmark/external/ponytail/skills/ponytail/SKILL.md \
  --format markdown \
  --json benchmark/results/live-claude.json
```

The printed live comparison table includes:

- estimated visible output tokens
- deltas vs baseline
- provider output tokens when available
- provider cost when available
- median latency
- report overhead

The JSON records include provider usage fields when Claude CLI returns them.

Generate a Markdown report from an existing live JSON:

```bash
python3 benchmark/bench.py \
  --report-from-json benchmark/results/live-claude.json \
  --report benchmark/results/live-claude.md
```

Live output includes two tables:

- response metrics: estimated output tokens, LOC, report overhead
- provider telemetry: successful calls, failures, provider tokens when available, cost when available, median latency

## Final-Report Suite

NoYap's core behavior is final-answer discipline. Run the final-report suite separately:

```bash
python3 benchmark/bench.py \
  --mode live \
  --suite final-report \
  --provider claude-cli \
  --runs 3 \
  --model claude-haiku-4-5-20251001 \
  --caveman-skill benchmark/external/caveman/skills/caveman/SKILL.md \
  --ponytail-skill benchmark/external/ponytail/skills/ponytail/SKILL.md \
  --format markdown \
  --json benchmark/results/live-final-report.json \
  --report benchmark/results/live-final-report.md
```

If a live comparison is published, include:

- provider
- model
- date
- run count
- external skill paths or commits
- token source: estimated table vs provider-reported records
- failed or timed-out calls

## Troubleshooting

`Not logged in · Please run /login`

: Authenticate Claude Code first. The benchmark cannot do this for you.

Empty-looking warnings

: Older NoYap versions only printed stderr. Current versions parse Claude's JSON stdout error and include it in warnings plus `benchmark/results/live-claude.json`.

## How Ponytail Does It

Ponytail uses two benchmark styles:

- Single-shot benchmark: promptfoo + provider APIs, repeated runs, median reported. It measures code LOC, token usage, cost, and latency from API telemetry.
- Agentic benchmark: headless Claude Code sessions in isolated workspaces. It measures `git diff` LOC, safety checks, tokens, cost, duration, and run metadata from Claude Code output.

NoYap live mode matches the single-shot comparison style. It does not yet implement Ponytail's full agentic workspace benchmark with isolated git workspaces and safety execution.
