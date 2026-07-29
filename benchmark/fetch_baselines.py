#!/usr/bin/env python3
"""Fetch external comparison repos for live benchmark runs."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from shutil import which


ROOT = Path(__file__).resolve().parent
EXTERNAL = ROOT / "external"


@dataclass(frozen=True)
class Repo:
    name: str
    url: str
    commit: str
    skill_path: str


REPOS = (
    Repo(
        name="caveman",
        url="https://github.com/JuliusBrussee/caveman.git",
        commit="0d95a81d35a9f2d123a5e9430d1cfc43d55f1bb0",
        skill_path="skills/caveman/SKILL.md",
    ),
    Repo(
        name="ponytail",
        url="https://github.com/DietrichGebert/ponytail.git",
        commit="1b2760d384c44e573a9d8c7a729fac616e5c3a76",
        skill_path="skills/ponytail/SKILL.md",
    ),
)


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def ensure_repo(repo: Repo, force: bool = False) -> Path:
    if which("git") is None:
        raise RuntimeError("git not found on PATH")
    EXTERNAL.mkdir(parents=True, exist_ok=True)
    target = EXTERNAL / repo.name
    if target.exists() and force:
        raise RuntimeError(f"{target} exists; remove it manually before using --force")
    if not target.exists():
        run(["git", "clone", repo.url, str(target)])
    run(["git", "fetch", "--depth", "1", "origin", repo.commit], cwd=target)
    run(["git", "checkout", "--detach", repo.commit], cwd=target)
    skill = target / repo.skill_path
    if not skill.exists():
        raise RuntimeError(f"missing expected skill file: {skill}")
    return skill


def live_command(model: str, runs: int) -> str:
    caveman = EXTERNAL / "caveman" / "skills" / "caveman" / "SKILL.md"
    ponytail = EXTERNAL / "ponytail" / "skills" / "ponytail" / "SKILL.md"
    return "\n".join(
        [
            "python3 benchmark/bench.py \\",
            "  --mode live \\",
            "  --provider claude-cli \\",
            f"  --runs {runs} \\",
            f"  --model {model} \\",
            f"  --caveman-skill {caveman} \\",
            f"  --ponytail-skill {ponytail} \\",
            "  --format markdown \\",
            "  --json benchmark/results/live-claude.json",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch external benchmark baselines")
    parser.add_argument("--model", default="claude-haiku-4-5-20251001")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--force", action="store_true", help="reserved; refuses to overwrite existing clones")
    args = parser.parse_args(argv)

    try:
        for repo in REPOS:
            skill = ensure_repo(repo, force=args.force)
            print(f"{repo.name}: {skill}")
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print()
    print("Run live benchmark:")
    print(live_command(args.model, args.runs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
