import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import install  # noqa: E402


class InstallTests(unittest.TestCase):
    def run_install(self, cfg, *args):
        return install.main(["--config-dir", str(cfg), *args])

    def test_skill_only(self):
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp)
            self.run_install(cfg)
            self.assertTrue((cfg / "skills" / "noyap" / "SKILL.md").exists())
            self.assertFalse((cfg / "settings.json").exists())

    def test_with_hook_preserves_existing_settings(self):
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp)
            (cfg / "settings.json").write_text(json.dumps({
                "model": "sonnet",
                "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "echo other"}]}]},
            }), encoding="utf-8")
            self.run_install(cfg, "--with-hook")
            self.assertTrue((cfg / "hooks" / "noyap-hook.sh").exists())
            settings = json.loads((cfg / "settings.json").read_text(encoding="utf-8"))
            self.assertEqual(settings["model"], "sonnet")
            cmds = [e["command"] for g in settings["hooks"]["SessionStart"] for e in g["hooks"]]
            self.assertIn("echo other", cmds)
            self.assertTrue(any("noyap-hook.sh" in c for c in cmds))

    def test_hook_is_idempotent(self):
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp)
            self.run_install(cfg, "--with-hook")
            self.run_install(cfg, "--with-hook")
            settings = json.loads((cfg / "settings.json").read_text(encoding="utf-8"))
            noyap = [e for g in settings["hooks"]["SessionStart"] for e in g["hooks"] if "noyap-hook.sh" in e["command"]]
            self.assertEqual(len(noyap), 1)

    def test_uninstall_strips_only_noyap(self):
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp)
            (cfg / "settings.json").write_text(json.dumps({
                "model": "sonnet",
                "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "echo other"}]}]},
            }), encoding="utf-8")
            self.run_install(cfg, "--with-hook")
            self.run_install(cfg, "--uninstall")
            self.assertFalse((cfg / "skills" / "noyap").exists())
            self.assertFalse((cfg / "hooks" / "noyap-hook.sh").exists())
            settings = json.loads((cfg / "settings.json").read_text(encoding="utf-8"))
            self.assertEqual(settings["model"], "sonnet")
            cmds = [e["command"] for g in settings["hooks"]["SessionStart"] for e in g["hooks"]]
            self.assertEqual(cmds, ["echo other"])

    def test_invalid_settings_json_refuses(self):
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp)
            (cfg / "settings.json").write_text("{ not json", encoding="utf-8")
            with self.assertRaises(SystemExit):
                self.run_install(cfg, "--with-hook")

    def test_dry_run_writes_nothing(self):
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp)
            self.run_install(cfg, "--with-hook", "--dry-run")
            self.assertFalse((cfg / "skills").exists())
            self.assertFalse((cfg / "settings.json").exists())


if __name__ == "__main__":
    unittest.main()
