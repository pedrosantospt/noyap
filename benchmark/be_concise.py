#!/usr/bin/env python3
"""Does a literal "be concise" instruction actually reduce output tokens?

Runs the final-report task suite twice per arm through the Claude CLI and
compares provider output tokens for two arms:

  baseline    no system prompt at all
  be_concise  system prompt: "Be concise. Keep your answer short."

This is a standalone experiment, separate from bench.py. Its baseline numbers
use a different run count and are NOT comparable to the bench.py tables --
read it on its own terms.

Usage:
    python3 benchmark/be_concise.py            # all 5 models, 2 runs
    python3 benchmark/be_concise.py --runs 3 --models claude-sonnet-5

Needs an authenticated Claude CLI on PATH.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_MODELS = [
    "claude-haiku-4-5",
    "claude-sonnet-5",
    "claude-opus-4-8",
    "claude-fable-5",
    "claude-opus-5",
]
BE_CONCISE = "Be concise. Keep your answer short."
TASKS_PATH = Path(__file__).with_name("tasks-final-report.json")


def output_tokens(prompt: str, system: str | None, model: str) -> int:
    cmd = ["claude", "-p", "--output-format", "json", "--model", model]
    if system:
        cmd += ["--system-prompt", system]
    cmd.append(prompt)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        data = json.loads(proc.stdout)
        return int((data.get("usage") or {}).get("output_tokens") or 0)
    except Exception as exc:  # noqa: BLE001 - report and continue
        sys.stderr.write(f"  err {model}: {str(exc)[:80]}\n")
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    args = ap.parse_args()

    tasks = json.loads(TASKS_PATH.read_text())["tasks"]
    arms = {"baseline": None, "be_concise": BE_CONCISE}

    results: dict[tuple[str, str], int] = {}
    for model in args.models:
        for arm, system in arms.items():
            total = 0
            for _ in range(args.runs):
                for task in tasks:
                    total += output_tokens(task["prompt"], system, model)
            results[(model, arm)] = total
            sys.stderr.write(f"{model} {arm}: {total}\n")
            sys.stderr.flush()

    print(f"\n=== literal 'be concise' vs baseline "
          f"(provider output tokens, {args.runs} runs x {len(tasks)} tasks) ===")
    print(f"{'model':<22} {'baseline':>9} {'be_concise':>11} {'change':>8}")
    for model in args.models:
        base = results[(model, "baseline")]
        conc = results[(model, "be_concise")]
        pct = (conc - base) / base * 100 if base else 0.0
        verdict = "MORE" if pct > 2 else ("fewer" if pct < -2 else "~same")
        print(f"{model:<22} {base:>9} {conc:>11} {pct:>+7.1f}%  {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
