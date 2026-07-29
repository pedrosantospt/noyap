# Changelog

## 0.1.0 — initial release

- Result-first output protocol: answer first, prove only what ran, flag only specific risk, ask once, then stop.
- Two-cut engine (remove whole sections, then tighten what remains) with `tiny` / `normal` / `full` budgets.
- Proof gate and risk gate for verification honesty.
- Persistence (anti-drift), `/noyap` activation, and off-switch.
- Adapters for Cursor, Windsurf, and GitHub Copilot.
- Claude Code installer (`install.py`) with an optional always-on `SessionStart` hook.
- Deterministic fixture benchmark plus a live five-model benchmark (Haiku, Sonnet, Opus 4.8, Fable, Opus 5) with committed reports and provenance.
- Real before/after model output in `examples/`.
