# Competitive Notes

Inspected on 2026-07-07.

## Repositories Inspected

| Project | URL | Branch | Commit |
|---|---|---|---|
| Caveman | https://github.com/JuliusBrussee/caveman | main | `0d95a81d35a9f2d123a5e9430d1cfc43d55f1bb0` |
| Ponytail | https://github.com/DietrichGebert/ponytail | main | `1b2760d384c44e573a9d8c7a729fac616e5c3a76` |
| Mimocode-ponytail | https://github.com/pavnxet/Mimocode-ponytail | main | `75a810e88f782c3b8b0eba3c24f42977c4b0be1a` |

`DietrichGebert/ponytail` is treated as canonical: exact repo name, homepage, active plugin layout, current benchmark writeups, and the derived repo credits it.

## Caveman

- Structure: multi-agent/plugin repo with `skills/`, `commands/`, `src/hooks/`, `.codex/`, `.claude-plugin/`, `benchmarks/`, `evals/`, installer scripts, docs, and tests.
- Core behavior: compresses answer prose, preserves exact code/commands/errors, supports intensity levels and language preservation.
- Integrations: Claude Code plugin, Codex config, Gemini extension, Cursor/Windsurf/Cline-style rules via installer, commands, hooks, statusline, MCP shrink tooling.
- Benchmark code: `benchmarks/run.py` calls Anthropic API; `evals/llm_run.py` calls Claude CLI; `evals/measure.py` reads committed snapshots.
- Benchmark tasks: 10 explanation/debugging/setup/refactor/security/devops prompts in `benchmarks/prompts.json`; eval prompts are 10 concise technical questions.
- Fixtures/results: committed `evals/snapshots/results.json`; `benchmarks/results/` only has `.gitkeep` in inspected commit.
- Token methodology: API benchmark uses provider-reported Anthropic `output_tokens`; eval measurement uses `tiktoken` `o200k_base` as an approximation for Claude output.
- LOC methodology: not the primary benchmark metric; result table is token-focused.
- Run methodology: API script defaults to 3 trials per prompt per mode, median per prompt, average savings; eval snapshot is single run per arm, then median/mean/min/max/stdev savings vs terse control.
- Aggregation: median per prompt for API runs; mean average savings in README table; eval reports median, mean, min, max, stdev.
- Cost/latency: API benchmark records token usage only; repo has stats tooling for session usage, but cost/latency are not central in the inspected benchmark code.
- Visual positioning: strong meme branding, rock/cave assets, playful compressed-language identity.
- Useful patterns: explicit honest-number warning, provider vs approximate token distinction, committed snapshots, dry-run mode, hash of skill file.
- Limitations: output-token reduction is not whole-session savings; skill prompt adds input tokens; approximate tokenizer is not provider usage; live API results depend on model/date.

## Ponytail

- Structure: plugin-oriented repo with `skills/`, rules for Cursor/Windsurf/Copilot/Cline/Kiro/OpenCode, hooks, commands, `benchmarks/`, agentic harness, examples, docs, assets, and tests.
- Core behavior: coding discipline that chooses the smallest sufficient implementation by checking codebase reuse, stdlib, native platform features, installed dependencies, and minimal code, while preserving safety checks.
- Integrations: Claude Code plugin, Codex plugin, Copilot plugin, Gemini/Antigravity extension, OpenCode plugin, Cursor/Windsurf/Cline/Kiro/Agents rules, MCP package.
- Benchmark code: promptfoo single-shot config; deterministic `loc.js`; correctness/behavior JS gates; Ollama local runner; Python agentic harness using headless Claude Code.
- Benchmark tasks: 5 single-shot coding tasks; 12 real-repo feature tickets; 7 surgical safety tasks with adversarial inputs.
- Fixtures/results: multiple markdown result artifacts in `benchmarks/results/`; agentic workspaces are generated locally and rescored offline.
- LOC methodology: single-shot counts non-blank, non-comment lines in fenced code blocks or bare code; agentic counts `git diff` added source lines, excludes tests from bloat, tracks test LOC separately.
- Token methodology: single-shot token/cost/latency from API telemetry; agentic token/cost/duration from Claude Code CLI JSON.
- Run methodology: single-shot uses repeated promptfoo runs, commonly 10 per cell; agentic uses isolated workspaces and fresh sessions, reported with `n=4` in current writeup.
- Aggregation: median for single-shot tables; mean across runs/tasks in agentic writeups, with per-task tables and limitations.
- Cost/latency: measured from provider/CLI telemetry in live runs; local Ollama runner records wall time.
- Visual positioning: character-led meme identity, one-line-code motif, prominent charts/assets.
- Useful patterns: benchmark critique handling, isolation checks for plugin contamination, deterministic selftests before API spend, clear safety-vs-size separation, provenance-rich result writeups.
- Limitations: single-shot baseline can inflate gains; agentic benchmark is one main model in current writeup; LLM judges are used for some subjective axes; safety tests are floors, not security proofs.

## Patterns To Adopt

- Label fixture, approximate, and provider-reported metrics separately.
- Keep deterministic fixture mode runnable without keys.
- Warn when provenance is incomplete.
- Preserve raw task definitions and benchmark code.
- Make benchmark limitations visible near the numbers.
- Use stable row ordering and explicit aggregation methods.

## Patterns To Avoid

- No copied slogans, voice, examples, visuals, or distinctive phrasing.
- No unsupported superiority claims.
- No mixing estimated tokens with provider-reported usage.
- No silent comparison between incompatible live and fixture metrics.
- No hiding benchmark contamination or fixture provenance gaps.

## How NoYap Remains Distinct

NoYap is not a code-minimalism ladder and not stylized compressed speech. It is an output protocol: answer first, prove only when verified, state risk only when specific, ask once when blocked, and stop. It targets final-response waste across code, research, planning, troubleshooting, recommendations, and factual answers while preserving safety and verification honesty.
