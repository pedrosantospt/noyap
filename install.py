#!/usr/bin/env python3
"""Install NoYap into a Claude Code config directory.

Default: copy the skill so Claude Code can load it on demand.
--with-hook: also wire a SessionStart hook so NoYap is active every session.

Stdlib only. Never writes outside the chosen config dir. settings.json is
backed up before any change, and the hook merge is idempotent.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
SKILL_SRC = REPO / "skills" / "noyap" / "SKILL.md"
HOOK_SRC = REPO / "hooks" / "noyap-hook.sh"
HOOK_MARKER = "noyap-hook.sh"  # idempotency / uninstall key


def default_config_dir() -> Path:
    env = os.environ.get("CLAUDE_CONFIG_DIR")
    return Path(env).expanduser() if env else Path.home() / ".claude"


def load_settings(path: Path) -> dict:
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON ({exc}). Fix or move it, then retry.")
    return data if isinstance(data, dict) else {}


def session_start_groups(settings: dict) -> list:
    hooks = settings.setdefault("hooks", {})
    groups = hooks.setdefault("SessionStart", [])
    if not isinstance(groups, list):
        raise SystemExit("error: settings.json hooks.SessionStart is not a list; refusing to touch it.")
    return groups


def hook_present(settings: dict) -> bool:
    for group in settings.get("hooks", {}).get("SessionStart", []) or []:
        for entry in (group or {}).get("hooks", []) or []:
            if HOOK_MARKER in str(entry.get("command", "")):
                return True
    return False


def add_hook(settings: dict, command: str) -> None:
    if hook_present(settings):
        return
    session_start_groups(settings).append({"hooks": [{"type": "command", "command": command}]})


def strip_hook(settings: dict) -> None:
    groups = settings.get("hooks", {}).get("SessionStart")
    if not isinstance(groups, list):
        return
    kept = []
    for group in groups:
        entries = [e for e in (group or {}).get("hooks", []) or [] if HOOK_MARKER not in str(e.get("command", ""))]
        if entries:
            kept.append({**group, "hooks": entries})
    if kept:
        settings["hooks"]["SessionStart"] = kept
    else:
        settings["hooks"].pop("SessionStart", None)
        if not settings["hooks"]:
            settings.pop("hooks", None)


def write_settings(path: Path, settings: dict, dry: bool) -> None:
    if dry:
        print(f"  would write {path}")
        return
    if path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Install NoYap into a Claude Code config dir.")
    p.add_argument("--config-dir", type=Path, default=default_config_dir(),
                   help="Claude Code config dir (default: $CLAUDE_CONFIG_DIR or ~/.claude)")
    p.add_argument("--with-hook", action="store_true",
                   help="also wire a SessionStart hook so NoYap is active every session")
    p.add_argument("--uninstall", action="store_true", help="remove the skill and hook")
    p.add_argument("--dry-run", action="store_true", help="print actions without writing")
    args = p.parse_args(argv)

    if not SKILL_SRC.exists():
        raise SystemExit(f"error: {SKILL_SRC} not found; run from a NoYap checkout.")

    cfg = args.config_dir.expanduser()
    skill_dst = cfg / "skills" / "noyap" / "SKILL.md"
    hook_dst = cfg / "hooks" / "noyap-hook.sh"
    settings_path = cfg / "settings.json"
    dry = args.dry_run

    if args.uninstall:
        print(f"Uninstalling NoYap from {cfg}")
        if skill_dst.parent.exists():
            print(f"  remove {skill_dst.parent}")
            if not dry:
                shutil.rmtree(skill_dst.parent, ignore_errors=True)
        if hook_dst.exists():
            print(f"  remove {hook_dst}")
            if not dry:
                hook_dst.unlink()
        if settings_path.exists():
            settings = load_settings(settings_path)
            if hook_present(settings):
                print("  strip SessionStart hook from settings.json")
                strip_hook(settings)
                write_settings(settings_path, settings, dry)
        print("Done." if not dry else "Dry run — nothing written.")
        return 0

    print(f"Installing NoYap into {cfg}")
    print(f"  copy skill -> {skill_dst}")
    if not dry:
        skill_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SKILL_SRC, skill_dst)

    if args.with_hook:
        print(f"  copy hook  -> {hook_dst}")
        if not dry:
            hook_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(HOOK_SRC, hook_dst)
            hook_dst.chmod(0o755)
        settings = load_settings(settings_path)
        if hook_present(settings):
            print("  SessionStart hook already present — skipping")
        else:
            print("  add SessionStart hook to settings.json")
            add_hook(settings, f"sh {hook_dst}")
            write_settings(settings_path, settings, dry)

    print("Done." if not dry else "Dry run — nothing written.")
    if not args.with_hook:
        print('Tip: re-run with --with-hook to keep NoYap active every session.')
    return 0


if __name__ == "__main__":
    sys.exit(main())
