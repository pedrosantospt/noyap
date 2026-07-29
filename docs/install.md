# Install & use NoYap

The full per-agent guide — installation, verification, controls, and uninstall.
For the quick version, see the [README](../README.md#install).

## Get the repo

```bash
git clone https://github.com/pedrosantospt/noyap
cd noyap
```

Or download the ZIP from the GitHub page (**Code → Download ZIP**).

**Prerequisites:** `git` to clone; `python3` only for the Claude Code installer.
The editor adapters need nothing but a file copy.

---

## Claude Code

### Easiest: install as a plugin (no clone, no Python)

From inside Claude Code:

```text
/plugin marketplace add pedrosantospt/noyap
/plugin install noyap@noyap
```

This loads the skill and wires the `SessionStart` hook, so NoYap is active every
session. Remove it with `/plugin uninstall noyap@noyap`. No files to clone, no
Python needed.

### Alternative: the stdlib installer (from a clone)

Prefer a manual setup, or scripting it? The installer is stdlib Python — no
dependencies.

```bash
python3 install.py               # A) skill only — load it on demand
python3 install.py --with-hook   # B) active every session   (recommended)
```

- **A) skill only** copies `skills/noyap/SKILL.md` to
  `~/.claude/skills/noyap/SKILL.md`. Claude Code discovers it and applies it when
  the task matches or you ask for it. Nothing runs automatically.
- **B) `--with-hook`** also installs `~/.claude/hooks/noyap-hook.sh` and adds a
  `SessionStart` hook to `~/.claude/settings.json` (backed up first; the merge is
  idempotent and only ever touches NoYap's own entry). Now the discipline is
  active from the first message of every session.

Flags:

- `--dry-run` — preview the exact changes, write nothing.
- `--config-dir DIR` — target a non-default config dir. `$CLAUDE_CONFIG_DIR` is
  also respected automatically.
- `--uninstall` — remove the skill and hook (see below).

Verify it took:

```bash
sh ~/.claude/hooks/noyap-hook.sh                 # prints the injected ruleset
grep -A3 SessionStart ~/.claude/settings.json    # shows the noyap-hook entry
```

Then open a **new** Claude Code session and ask anything — the reply should lead
with the result and skip the preamble.

---

## Editor adapters

Each is a single file copied into the project (or global config) you want it in.

### Cursor

```bash
mkdir -p your-project/.cursor/rules
cp .cursor/rules/noyap.mdc your-project/.cursor/rules/
```

It's `alwaysApply: true`, so it's on for that project. For every project, add it
to Cursor's global rules instead.

### Windsurf

```bash
mkdir -p your-project/.windsurf/rules
cp .windsurf/rules/noyap.md your-project/.windsurf/rules/
```

### GitHub Copilot

```bash
cp .github/copilot-instructions.md your-project/.github/copilot-instructions.md
```

Copilot reads repo-wide instructions from that path automatically.

### Codex / any agent with a system prompt

```bash
mkdir -p ~/.codex/skills/noyap
cp skills/noyap/SKILL.md ~/.codex/skills/noyap/SKILL.md
```

Or paste `skills/noyap/SKILL.md` into any agent's system-prompt / custom-
instructions box.

---

## Use it

Once active, controls you can type mid-chat:

| Type this | Effect |
|---|---|
| `/noyap tiny` | 1–3 lines |
| `/noyap normal` | default |
| `/noyap full` | spend the words (security, migrations, "give me detail") |
| `stop noyap` / `normal mode` | turn it off for the session |

Budgets: **tiny** (trivial confirmations), **normal** (default), **full**
(security, legal, migrations, destructive actions, explicit detail requests).

## See it working

Ask the same question with and without NoYap. Without: preamble + a recap of what
it just did. With: the answer on line one, `Not run.` instead of a fake
"tests pass," and a named risk instead of "there may be edge cases." Real
before/after pairs are in [`examples/`](../examples/).

## Uninstall

- Temporarily: say `stop noyap`.
- Claude Code, fully: `python3 install.py --uninstall` — removes the skill and
  hook, strips only NoYap's `SessionStart` entry, and leaves the rest of
  `settings.json` intact.
- Adapters: delete the file you copied.
