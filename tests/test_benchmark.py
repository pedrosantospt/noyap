import contextlib
import io
import json
from unittest import mock
import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmark"))

import bench  # noqa: E402


class BenchmarkTests(unittest.TestCase):
    def test_token_estimation(self):
        self.assertEqual(bench.estimate_tokens(""), 0)
        self.assertEqual(bench.estimate_tokens("abcd"), 1)
        self.assertEqual(bench.estimate_tokens("abcde"), 2)

    def test_fenced_code_extraction(self):
        text = "a\n```python\nprint(1)\n```\nb"
        self.assertEqual(bench.extract_code_blocks(text), ["print(1)\n"])

    def test_multiple_code_blocks(self):
        text = "```python\na=1\n```\ntext\n```ts\nconst b = 2\n```"
        self.assertEqual(bench.extract_code_blocks(text), ["a=1\n", "const b = 2\n"])

    def test_loc_counting(self):
        text = "```python\n\nx = 1\n\nprint(x)\n```"
        self.assertEqual(bench.count_loc_in_blocks(text), 2)

    def test_report_and_code_token_counting(self):
        text = "Fixed.\n```python\nprint('abcd')\n```\nNot run.\n"
        metrics = bench.measure_text(text)
        code = "print('abcd')\n"
        report = "Fixed.\n\nNot run.\n"
        self.assertEqual(metrics["code_tokens"], bench.estimate_tokens(code))
        self.assertEqual(metrics["report_tokens"], bench.estimate_tokens(report))

    def test_empty_output(self):
        metrics = bench.measure_text("")
        self.assertEqual(metrics["tokens"], 0)
        self.assertEqual(metrics["loc"], 0)
        self.assertEqual(metrics["report_tokens"], 0)

    def test_missing_fixture_handling(self):
        tasks = [{"id": "task-01"}]
        with tempfile.TemporaryDirectory() as tmp:
            fixtures = Path(tmp)
            for name in bench.ROW_ORDER:
                (fixtures / name).mkdir()
            (fixtures / "noyap" / "task-01.md").write_text("Fixed.\n", encoding="utf-8")
            rows, warnings = bench.run_fixture(tasks, fixtures)
        self.assertEqual([row.skill for row in rows], [bench.DISPLAY[name] for name in bench.ROW_ORDER])
        self.assertTrue(any("missing fixtures" in warning for warning in warnings))

    def test_malformed_task_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tasks.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(bench.BenchmarkError):
                bench.load_tasks(path)

    def test_task_suite_paths(self):
        self.assertEqual(bench.task_path_for_suite("coding").name, "tasks.json")
        self.assertEqual(bench.task_path_for_suite("final-report").name, "tasks-final-report.json")

    def test_stable_result_ordering(self):
        tasks = bench.load_tasks()
        rows, _warnings = bench.run_fixture(tasks)
        self.assertEqual([row.skill for row in rows], [bench.DISPLAY[name] for name in bench.ROW_ORDER])

    def test_zero_token_edge_case(self):
        rows = [
            bench.Metrics(
                skill="Empty",
                tasks=0,
                total_loc=0,
                median_loc_per_task=0,
                total_output_tokens=0,
                median_tokens_per_task=0,
                report_tokens=0,
                report_overhead=0,
                total_output_characters=0,
                code_tokens=0,
                total_response_lines=0,
                median_response_lines_per_task=0,
            )
        ]
        self.assertIn("0.0%", bench.format_table(rows))

    def test_provenance_warning_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "provenance.json"
            path.write_text(
                json.dumps({"baselines": [{"name": "External", "data_origin": "synthetic", "provenance_complete": False}]}),
                encoding="utf-8",
            )
            warnings = bench.warn_provenance(path)
        self.assertEqual(warnings, ["incomplete provenance for External: synthetic"])

    def test_main_writes_markdown_and_warnings(self):
        stderr = io.StringIO()
        stdout = io.StringIO()
        with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
            code = bench.main(["--format", "markdown"])
        self.assertEqual(code, 0)
        self.assertIn("| Skill | Tasks |", stdout.getvalue())
        self.assertIn("warning: incomplete provenance", stderr.getvalue())

    def test_extract_result_text_from_cli_json(self):
        self.assertEqual(bench.extract_result_text({"result": "Fixed."}), "Fixed.")
        self.assertEqual(
            bench.extract_result_text({"message": {"content": [{"text": "A"}, {"text": "B"}]}}),
            "A\nB",
        )

    def test_flatten_usage_from_cli_json(self):
        usage = bench.flatten_usage(
            {
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 3,
                    "cache_creation": {"ephemeral_5m_input_tokens": 4, "ephemeral_1h_input_tokens": 6},
                    "cache_read_input_tokens": 8,
                },
                "total_cost_usd": 0.01,
                "duration_ms": 123,
            }
        )
        self.assertEqual(usage["input_tokens"], 10)
        self.assertEqual(usage["output_tokens"], 3)
        self.assertEqual(usage["cache_creation_input_tokens"], 10)
        self.assertEqual(usage["cache_creation_5m_input_tokens"], 4)
        self.assertEqual(usage["cache_creation_1h_input_tokens"], 6)
        self.assertEqual(usage["cache_read_input_tokens"], 8)
        self.assertEqual(usage["total_cost_usd"], 0.01)
        self.assertEqual(usage["duration_ms"], 123)

    def test_run_claude_cli_parses_json_error_stdout(self):
        completed = mock.Mock()
        completed.returncode = 1
        completed.stdout = json.dumps({"is_error": True, "result": "Not logged in", "usage": {"output_tokens": 0}})
        completed.stderr = ""
        with mock.patch.object(bench, "which", return_value="/bin/claude"), mock.patch.object(bench.subprocess, "run", return_value=completed):
            result = bench.run_claude_cli("Say OK", None, None, 10)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "Not logged in")
        self.assertEqual(result["usage"]["output_tokens"], 0)

    def test_build_live_arms_requires_external_skill_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.md"
            second = Path(tmp) / "second.md"
            first.write_text("first", encoding="utf-8")
            second.write_text("second", encoding="utf-8")
            arms = bench.build_live_arms(first, second)
        self.assertEqual(arms[bench.ROW_ORDER[0]], None)
        self.assertEqual(arms[bench.ROW_ORDER[1]], "first")
        self.assertEqual(arms[bench.ROW_ORDER[2]], "second")
        self.assertIn("NoYap", arms[bench.ROW_ORDER[3]])

    def test_live_mode_missing_skill_path_returns_error(self):
        stderr = io.StringIO()
        stdout = io.StringIO()
        first_flag = "--" + bench.ROW_ORDER[1] + "-skill"
        second_flag = "--" + bench.ROW_ORDER[2] + "-skill"
        with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
            code = bench.main(["--mode", "live", first_flag, "missing-a.md", second_flag, "missing-b.md"])
        self.assertEqual(code, 1)
        self.assertIn("skill file not found", stderr.getvalue())

    def test_live_mode_requires_external_skill_paths(self):
        stderr = io.StringIO()
        stdout = io.StringIO()
        with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
            code = bench.main(["--mode", "live"])
        self.assertEqual(code, 1)
        self.assertIn("required for live comparison", stderr.getvalue())

    def test_live_mode_returns_nonzero_on_failed_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.md"
            second = Path(tmp) / "second.md"
            out = Path(tmp) / "live.json"
            first.write_text("first", encoding="utf-8")
            second.write_text("second", encoding="utf-8")
            failed = {"ok": False, "text": "Not logged in", "error": "Not logged in", "stderr": "", "returncode": 1, "latency_ms": 1, "usage": {}}
            first_flag = "--" + bench.ROW_ORDER[1] + "-skill"
            second_flag = "--" + bench.ROW_ORDER[2] + "-skill"
            with mock.patch.object(bench, "run_claude_cli", return_value=failed), contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                code = bench.main(["--mode", "live", "--runs", "1", first_flag, str(first), second_flag, str(second), "--json", str(out)])
        self.assertEqual(code, 1)

    def test_live_telemetry_table(self):
        records = [
            {
                "arm": bench.ROW_ORDER[0],
                "ok": True,
                "usage": {"input_tokens": 10, "output_tokens": 5, "total_cost_usd": 0.002},
                "latency_ms": 100,
            },
            {
                "arm": bench.ROW_ORDER[0],
                "ok": False,
                "usage": {},
                "latency_ms": 200,
            },
        ]
        table = bench.format_live_telemetry(records, markdown=True)
        self.assertIn("Provider output tokens", table)
        self.assertIn("| Baseline | 1 | 1 | 10 | 5 | 0.002000 | 100 |", table)

    def test_simple_api_cost_check(self):
        records = [
            {
                "arm": bench.ROW_ORDER[0],
                "ok": True,
                "usage": {"input_tokens": 1000, "output_tokens": 2000, "total_cost_usd": 0.025},
                "latency_ms": 100,
            }
        ]
        rows = bench.cost_sanity_rows(records, input_price=1.0, output_price=5.0)
        self.assertEqual(rows[0]["simple_cost_usd"], 0.011)
        self.assertAlmostEqual(rows[0]["reported_to_simple"], 0.025 / 0.011)
        table = bench.format_cost_sanity(records, markdown=True, input_price=1.0, output_price=5.0)
        self.assertIn("Simple API cost USD", table)
        self.assertIn("2.27x", table)
        note = bench.cost_sanity_note(records, input_price=1.0, output_price=5.0)
        self.assertIn("do not match", note)

    def test_live_comparison_table_includes_deltas(self):
        rows = [
            bench.Metrics("Baseline", 1, 0, 0, 100, 100, 80, 0.8, 400, 20, 10, 10),
            bench.Metrics(bench.DISPLAY[bench.ROW_ORDER[1]], 1, 0, 0, 50, 50, 20, 0.4, 200, 10, 5, 5),
            bench.Metrics(bench.DISPLAY[bench.ROW_ORDER[2]], 1, 0, 0, 70, 70, 50, 0.7, 280, 12, 6, 6),
            bench.Metrics("NoYap", 1, 0, 0, 40, 40, 10, 0.25, 160, 8, 3, 3),
        ]
        records = [
            {"arm": "baseline", "ok": True, "usage": {"output_tokens": 100, "total_cost_usd": 1}, "latency_ms": 100},
            {"arm": bench.ROW_ORDER[1], "ok": True, "usage": {"output_tokens": 40, "total_cost_usd": 0.5}, "latency_ms": 50},
            {"arm": bench.ROW_ORDER[2], "ok": True, "usage": {"output_tokens": 80, "total_cost_usd": 0.8}, "latency_ms": 80},
            {"arm": "noyap", "ok": True, "usage": {"output_tokens": 60, "total_cost_usd": 0.6}, "latency_ms": 60},
        ]
        table = bench.format_live_comparison(rows, records, markdown=True)
        self.assertIn("Est vs baseline", table)
        self.assertIn("Provider output tokens", table)
        self.assertIn("+60.0%", table)

    def test_report_from_existing_json(self):
        payload = {
            "provider": "claude-cli",
            "model": "test-model",
            "runs": 1,
            "generated_at": "2026-07-08T00:00:00+00:00",
            "warnings": [],
            "rows": [
                {
                    "skill": "Baseline",
                    "tasks": 1,
                    "total_loc": 0,
                    "median_loc_per_task": 0,
                    "total_output_tokens": 100,
                    "median_tokens_per_task": 100,
                    "report_tokens": 80,
                    "report_overhead": 0.8,
                    "total_output_characters": 400,
                    "code_tokens": 20,
                    "total_response_lines": 10,
                    "median_response_lines_per_task": 10,
                }
            ],
            "records": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "live.json"
            report = Path(tmp) / "live.md"
            source.write_text(json.dumps(payload), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                code = bench.main(["--report-from-json", str(source), "--report", str(report)])
            content = report.read_text(encoding="utf-8")
        self.assertEqual(code, 0)
        self.assertIn("# Live Claude Benchmark", content)
        self.assertIn("Cost Sanity Check", content)
        self.assertIn("test-model", content)


if __name__ == "__main__":
    unittest.main()
