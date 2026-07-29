#!/usr/bin/env python3
"""Deterministic fixture benchmark for compact agent outputs."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from shutil import which


ROOT = Path(__file__).resolve().parent
TASKS_PATH = ROOT / "tasks.json"
FINAL_REPORT_TASKS_PATH = ROOT / "tasks-final-report.json"
PROVENANCE_PATH = ROOT / "provenance.json"
FIXTURES_DIR = ROOT / "fixtures"
NOYAP_SKILL_PATH = ROOT.parent / "skills" / "noyap" / "SKILL.md"
ROW_ORDER = ("baseline", "caveman", "ponytail", "noyap")
DISPLAY = {"baseline": "Baseline", "caveman": "Caveman", "ponytail": "Ponytail", "noyap": "NoYap"}
FENCE_RE = re.compile(r"```[A-Za-z0-9_+.-]*[ \t]*\r?\n([\s\S]*?)```")
DEFAULT_INPUT_PRICE_USD_PER_MTOK = 1.0
DEFAULT_OUTPUT_PRICE_USD_PER_MTOK = 5.0


class BenchmarkError(Exception):
    """Input data is missing or malformed."""


@dataclass
class Metrics:
    skill: str
    tasks: int
    total_loc: int
    median_loc_per_task: float
    total_output_tokens: int
    median_tokens_per_task: float
    report_tokens: int
    report_overhead: float
    total_output_characters: int
    code_tokens: int
    total_response_lines: int
    median_response_lines_per_task: float


def estimate_tokens(text: str) -> int:
    """Deterministic heuristic: ceil(UTF-8 bytes / 4). Not provider usage."""
    if not text:
        return 0
    return math.ceil(len(text.encode("utf-8")) / 4)


def extract_code_blocks(text: str) -> list[str]:
    return [match.group(1) for match in FENCE_RE.finditer(text or "")]


def strip_code_blocks(text: str) -> str:
    return FENCE_RE.sub("", text or "")


def count_loc_in_blocks(text: str) -> int:
    return sum(1 for block in extract_code_blocks(text) for line in block.splitlines() if line.strip())


def load_tasks(path: Path = TASKS_PATH) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BenchmarkError(f"missing task file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BenchmarkError(f"malformed task file: {path}: {exc}") from exc
    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        raise BenchmarkError("task file must contain a tasks list")
    for task in tasks:
        if not isinstance(task, dict) or not task.get("id"):
            raise BenchmarkError("each task must be an object with an id")
    return tasks


def task_path_for_suite(suite: str) -> Path:
    if suite == "coding":
        return TASKS_PATH
    if suite == "final-report":
        return FINAL_REPORT_TASKS_PATH
    raise BenchmarkError(f"unknown task suite: {suite}")


def load_fixture(skill: str, task_id: str, fixtures_dir: Path = FIXTURES_DIR) -> str | None:
    path = fixtures_dir / skill / f"{task_id}.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def response_line_count(text: str) -> int:
    return len((text or "").splitlines())


def measure_text(text: str) -> dict:
    code = "\n".join(extract_code_blocks(text))
    report = strip_code_blocks(text)
    return {
        "chars": len(text),
        "tokens": estimate_tokens(text),
        "loc": count_loc_in_blocks(text),
        "code_tokens": estimate_tokens(code),
        "report_tokens": estimate_tokens(report),
        "lines": response_line_count(text),
    }


def median(values: list[int]) -> float:
    if not values:
        return 0.0
    return float(statistics.median(values))


def warn_provenance(path: Path = PROVENANCE_PATH) -> list[str]:
    warnings: list[str] = []
    if not path.exists():
        return [f"missing provenance file: {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"malformed provenance file: {path}: {exc}"]
    for entry in data.get("baselines", []):
        name = entry.get("name", "unknown")
        if not entry.get("provenance_complete", False):
            warnings.append(f"incomplete provenance for {name}: {entry.get('data_origin', 'unknown')}")
    return warnings


def read_skill(path: Path | None, label: str) -> str | None:
    if path is None:
        return None
    if not path.exists():
        raise BenchmarkError(f"{label} skill file not found: {path}")
    return path.read_text(encoding="utf-8")


def build_live_arms(caveman_skill: Path | None, ponytail_skill: Path | None) -> dict[str, str | None]:
    if caveman_skill is None:
        raise BenchmarkError("--caveman-skill is required for live comparison")
    if ponytail_skill is None:
        raise BenchmarkError("--ponytail-skill is required for live comparison")
    return {
        "baseline": None,
        "caveman": read_skill(caveman_skill, "Caveman"),
        "ponytail": read_skill(ponytail_skill, "Ponytail"),
        "noyap": read_skill(NOYAP_SKILL_PATH, "NoYap"),
    }


def extract_result_text(data: dict) -> str:
    for key in ("result", "text", "content", "output"):
        value = data.get(key)
        if isinstance(value, str):
            return value
    message = data.get("message")
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    parts.append(item["text"])
            if parts:
                return "\n".join(parts)
    return ""


def flatten_usage(data: dict) -> dict:
    usage = data.get("usage")
    if not isinstance(usage, dict):
        usage = {}
    def pick(source: dict, key: str, fallback_source: dict | None = None):
        if key in source:
            return source[key]
        if fallback_source and key in fallback_source:
            return fallback_source[key]
        return None
    cache_creation = usage.get("cache_creation")
    if not isinstance(cache_creation, dict):
        cache_creation = {}
    cache_creation_total = pick(usage, "cache_creation_input_tokens", data)
    cache_creation_5m = cache_creation.get("ephemeral_5m_input_tokens")
    cache_creation_1h = cache_creation.get("ephemeral_1h_input_tokens")
    if cache_creation_total is None and (cache_creation_5m is not None or cache_creation_1h is not None):
        cache_creation_total = int(cache_creation_5m or 0) + int(cache_creation_1h or 0)
    return {
        "input_tokens": pick(usage, "input_tokens", data),
        "output_tokens": pick(usage, "output_tokens", data),
        "total_tokens": pick(usage, "total_tokens", data),
        "cache_creation_input_tokens": cache_creation_total,
        "cache_creation_5m_input_tokens": cache_creation_5m,
        "cache_creation_1h_input_tokens": cache_creation_1h,
        "cache_read_input_tokens": pick(usage, "cache_read_input_tokens", data),
        "total_cost_usd": pick(data, "total_cost_usd") if "total_cost_usd" in data else data.get("cost_usd"),
        "duration_ms": pick(data, "duration_ms") if "duration_ms" in data else data.get("duration_api_ms"),
        "num_turns": data.get("num_turns") if "num_turns" in data else None,
    }


def run_claude_cli(
    prompt: str,
    system_prompt: str | None,
    model: str | None,
    timeout: int,
    json_output: bool = True,
) -> dict:
    claude = which("claude")
    if claude is None:
        raise BenchmarkError("claude CLI not found on PATH")
    cmd = [claude, "-p"]
    if json_output:
        cmd += ["--output-format", "json"]
    if system_prompt:
        cmd += ["--system-prompt", system_prompt]
    if model:
        cmd += ["--model", model]
    cmd.append(prompt)

    started = time.perf_counter()
    completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    latency_ms = round((time.perf_counter() - started) * 1000)
    try:
        data = json.loads(completed.stdout) if json_output and completed.stdout.strip() else {}
    except json.JSONDecodeError:
        data = {}
    text = extract_result_text(data) if data else completed.stdout.strip()
    usage = flatten_usage(data) if data else {}
    is_error = bool(data.get("is_error")) if data else False
    error_message = text or completed.stderr.strip()
    if completed.returncode != 0:
        return {
            "ok": False,
            "text": text,
            "error": error_message,
            "stderr": completed.stderr.strip(),
            "returncode": completed.returncode,
            "latency_ms": latency_ms,
            "raw": data if data else completed.stdout,
            "usage": usage,
        }
    if is_error:
        return {
            "ok": False,
            "text": text,
            "error": error_message,
            "stderr": completed.stderr.strip(),
            "returncode": completed.returncode,
            "latency_ms": latency_ms,
            "raw": data if data else completed.stdout,
            "usage": usage,
        }
    return {
        "ok": True,
        "text": text,
        "error": "",
        "stderr": completed.stderr.strip(),
        "returncode": completed.returncode,
        "latency_ms": latency_ms,
        "raw": data if data else completed.stdout,
        "usage": usage,
    }


def run_fixture(tasks: list[dict], fixtures_dir: Path = FIXTURES_DIR) -> tuple[list[Metrics], list[str]]:
    warnings = warn_provenance()
    rows: list[Metrics] = []
    for skill in ROW_ORDER:
        per_task = []
        missing = []
        for task in tasks:
            task_id = task["id"]
            text = load_fixture(skill, task_id, fixtures_dir)
            if text is None:
                missing.append(task_id)
                continue
            per_task.append(measure_text(text))
        if missing:
            warnings.append(f"missing fixtures for {DISPLAY[skill]}: {', '.join(missing)}")
        total_tokens = sum(item["tokens"] for item in per_task)
        report_tokens = sum(item["report_tokens"] for item in per_task)
        rows.append(
            Metrics(
                skill=DISPLAY[skill],
                tasks=len(per_task),
                total_loc=sum(item["loc"] for item in per_task),
                median_loc_per_task=median([item["loc"] for item in per_task]),
                total_output_tokens=total_tokens,
                median_tokens_per_task=median([item["tokens"] for item in per_task]),
                report_tokens=report_tokens,
                report_overhead=(report_tokens / total_tokens) if total_tokens else 0.0,
                total_output_characters=sum(item["chars"] for item in per_task),
                code_tokens=sum(item["code_tokens"] for item in per_task),
                total_response_lines=sum(item["lines"] for item in per_task),
                median_response_lines_per_task=median([item["lines"] for item in per_task]),
            )
        )
    return rows, warnings


def aggregate_live(results: list[dict]) -> list[Metrics]:
    rows: list[Metrics] = []
    for skill in ROW_ORDER:
        outputs = [item for item in results if item["arm"] == skill and item["ok"]]
        per_output = [measure_text(item["text"]) for item in outputs]
        total_tokens = sum(item["tokens"] for item in per_output)
        report_tokens = sum(item["report_tokens"] for item in per_output)
        rows.append(
            Metrics(
                skill=DISPLAY[skill],
                tasks=len({item["task_id"] for item in outputs}),
                total_loc=sum(item["loc"] for item in per_output),
                median_loc_per_task=median([item["loc"] for item in per_output]),
                total_output_tokens=total_tokens,
                median_tokens_per_task=median([item["tokens"] for item in per_output]),
                report_tokens=report_tokens,
                report_overhead=(report_tokens / total_tokens) if total_tokens else 0.0,
                total_output_characters=sum(item["chars"] for item in per_output),
                code_tokens=sum(item["code_tokens"] for item in per_output),
                total_response_lines=sum(item["lines"] for item in per_output),
                median_response_lines_per_task=median([item["lines"] for item in per_output]),
            )
        )
    return rows


def run_live_claude_cli(
    tasks: list[dict],
    runs: int,
    model: str | None,
    timeout: int,
    caveman_skill: Path | None,
    ponytail_skill: Path | None,
) -> tuple[list[Metrics], list[dict], list[str]]:
    if runs < 1:
        raise BenchmarkError("--runs must be >= 1")
    arms = build_live_arms(caveman_skill, ponytail_skill)
    results: list[dict] = []
    warnings: list[str] = []
    for run_index in range(1, runs + 1):
        for task in tasks:
            for arm in ROW_ORDER:
                result = run_claude_cli(
                    prompt=task["prompt"],
                    system_prompt=arms[arm],
                    model=model,
                    timeout=timeout,
                )
                record = {
                    "run": run_index,
                    "task_id": task["id"],
                    "task_title": task.get("title"),
                    "arm": arm,
                    "skill": DISPLAY[arm],
                    "ok": result["ok"],
                    "text": result["text"],
                    "error": result["error"],
                    "stderr": result["stderr"],
                    "returncode": result["returncode"],
                    "latency_ms": result["latency_ms"],
                    "usage": result["usage"],
                }
                raw = result.get("raw")
                if isinstance(raw, dict) and isinstance(raw.get("usage"), dict):
                    record["raw_usage"] = raw["usage"]
                if not result["ok"]:
                    warnings.append(f"{DISPLAY[arm]} {task['id']} run {run_index} failed: {result['error'][:160]}")
                results.append(record)
    return aggregate_live(results), results, warnings


def format_table(rows: list[Metrics], markdown: bool = False) -> str:
    headers = [
        "Skill",
        "Tasks",
        "Total LOC",
        "Median LOC/task",
        "Total output tokens",
        "Median tokens/task",
        "Report tokens",
        "Report overhead",
    ]
    body = [
        [
            row.skill,
            str(row.tasks),
            str(row.total_loc),
            f"{row.median_loc_per_task:g}",
            str(row.total_output_tokens),
            f"{row.median_tokens_per_task:g}",
            str(row.report_tokens),
            f"{row.report_overhead:.1%}",
        ]
        for row in rows
    ]
    if markdown:
        lines = ["| " + " | ".join(headers) + " |"]
        lines.append("|" + "|".join(["---"] * len(headers)) + "|")
        lines.extend("| " + " | ".join(row) + " |" for row in body)
        return "\n".join(lines)
    widths = [len(h) for h in headers]
    for row in body:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]
    lines = ["  ".join(cell.ljust(width) for cell, width in zip(headers, widths))]
    lines.append("  ".join("-" * width for width in widths))
    lines.extend("  ".join(cell.ljust(width) for cell, width in zip(row, widths)) for row in body)
    return "\n".join(lines)


def format_live_telemetry(records: list[dict], markdown: bool = False) -> str:
    headers = ["Skill", "Successful calls", "Failures", "Provider input tokens", "Provider output tokens", "Cost USD", "Median latency ms"]
    body = []
    for arm in ROW_ORDER:
        arm_records = [record for record in records if record["arm"] == arm]
        successes = [record for record in arm_records if record["ok"]]
        failures = len(arm_records) - len(successes)
        input_tokens = sum(int(record["usage"].get("input_tokens") or 0) for record in successes)
        output_tokens = sum(int(record["usage"].get("output_tokens") or 0) for record in successes)
        costs = [float(record["usage"].get("total_cost_usd") or 0.0) for record in successes]
        latencies = [int(record["latency_ms"]) for record in successes]
        body.append(
            [
                DISPLAY[arm],
                str(len(successes)),
                str(failures),
                str(input_tokens) if input_tokens else "n/a",
                str(output_tokens) if output_tokens else "n/a",
                f"{sum(costs):.6f}" if any(costs) else "n/a",
                f"{median(latencies):g}" if latencies else "n/a",
            ]
        )
    if markdown:
        lines = ["| " + " | ".join(headers) + " |"]
        lines.append("|" + "|".join(["---"] * len(headers)) + "|")
        lines.extend("| " + " | ".join(row) + " |" for row in body)
        return "\n".join(lines)
    widths = [len(h) for h in headers]
    for row in body:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]
    lines = ["  ".join(cell.ljust(width) for cell, width in zip(headers, widths))]
    lines.append("  ".join("-" * width for width in widths))
    lines.extend("  ".join(cell.ljust(width) for cell, width in zip(row, widths)) for row in body)
    return "\n".join(lines)


def pct_delta(value: float | int | None, baseline: float | int | None, lower_is_better: bool = True) -> str:
    if value is None or baseline in (None, 0):
        return "n/a"
    delta = (float(value) - float(baseline)) / float(baseline)
    if lower_is_better:
        delta *= -1
    sign = "+" if delta >= 0 else "-"
    return f"{sign}{abs(delta) * 100:.1f}%"


def live_provider_summary(records: list[dict]) -> dict[str, dict]:
    summary: dict[str, dict] = {}
    for arm in ROW_ORDER:
        arm_records = [record for record in records if record["arm"] == arm]
        successes = [record for record in arm_records if record["ok"]]
        summary[arm] = {
            "calls": len(successes),
            "failures": len(arm_records) - len(successes),
            "provider_input_tokens": sum(int(record["usage"].get("input_tokens") or 0) for record in successes),
            "provider_output_tokens": sum(int(record["usage"].get("output_tokens") or 0) for record in successes),
            "cost_usd": sum(float(record["usage"].get("total_cost_usd") or 0.0) for record in successes),
            "median_latency_ms": median([int(record["latency_ms"]) for record in successes]) if successes else 0.0,
        }
    return summary


def simple_api_cost_usd(input_tokens: int, output_tokens: int, input_price: float, output_price: float) -> float:
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000


def pricing_from_payload(payload: dict | None = None) -> tuple[float, float]:
    pricing = (payload or {}).get("pricing")
    if not isinstance(pricing, dict):
        pricing = {}
    input_price = pricing.get("input_usd_per_mtok", DEFAULT_INPUT_PRICE_USD_PER_MTOK)
    output_price = pricing.get("output_usd_per_mtok", DEFAULT_OUTPUT_PRICE_USD_PER_MTOK)
    return float(input_price), float(output_price)


def cost_sanity_rows(
    records: list[dict],
    input_price: float = DEFAULT_INPUT_PRICE_USD_PER_MTOK,
    output_price: float = DEFAULT_OUTPUT_PRICE_USD_PER_MTOK,
) -> list[dict]:
    provider = live_provider_summary(records)
    rows = []
    for arm in ROW_ORDER:
        stats = provider.get(arm, {})
        input_tokens = int(stats.get("provider_input_tokens") or 0)
        output_tokens = int(stats.get("provider_output_tokens") or 0)
        reported_cost = float(stats.get("cost_usd") or 0.0)
        expected_cost = simple_api_cost_usd(input_tokens, output_tokens, input_price, output_price)
        rows.append(
            {
                "skill": DISPLAY[arm],
                "provider_input_tokens": input_tokens,
                "provider_output_tokens": output_tokens,
                "reported_cost_usd": reported_cost,
                "simple_cost_usd": expected_cost,
                "reported_to_simple": (reported_cost / expected_cost) if expected_cost else 0.0,
            }
        )
    return rows


def format_cost_sanity(
    records: list[dict],
    markdown: bool = False,
    input_price: float = DEFAULT_INPUT_PRICE_USD_PER_MTOK,
    output_price: float = DEFAULT_OUTPUT_PRICE_USD_PER_MTOK,
) -> str:
    headers = [
        "Skill",
        "Provider input tokens",
        "Provider output tokens",
        "Reported cost USD",
        "Simple API cost USD",
        "Reported/simple",
    ]
    body = []
    for row in cost_sanity_rows(records, input_price, output_price):
        body.append(
            [
                row["skill"],
                str(row["provider_input_tokens"]) if row["provider_input_tokens"] else "n/a",
                str(row["provider_output_tokens"]) if row["provider_output_tokens"] else "n/a",
                f"{row['reported_cost_usd']:.6f}" if row["reported_cost_usd"] else "n/a",
                f"{row['simple_cost_usd']:.6f}" if row["simple_cost_usd"] else "n/a",
                f"{row['reported_to_simple']:.2f}x" if row["reported_to_simple"] else "n/a",
            ]
        )
    if markdown:
        lines = ["| " + " | ".join(headers) + " |"]
        lines.append("|" + "|".join(["---"] * len(headers)) + "|")
        lines.extend("| " + " | ".join(row) + " |" for row in body)
        return "\n".join(lines)
    widths = [len(h) for h in headers]
    for row in body:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]
    lines = ["  ".join(cell.ljust(width) for cell, width in zip(headers, widths))]
    lines.append("  ".join("-" * width for width in widths))
    lines.extend("  ".join(cell.ljust(width) for cell, width in zip(row, widths)) for row in body)
    return "\n".join(lines)


def cost_sanity_note(
    records: list[dict],
    input_price: float = DEFAULT_INPUT_PRICE_USD_PER_MTOK,
    output_price: float = DEFAULT_OUTPUT_PRICE_USD_PER_MTOK,
    tolerance: float = 0.20,
) -> str:
    mismatches = []
    for row in cost_sanity_rows(records, input_price, output_price):
        ratio = row["reported_to_simple"]
        if ratio and abs(ratio - 1.0) > tolerance:
            mismatches.append(f"{row['skill']} {ratio:.2f}x")
    if not mismatches:
        return "Reported costs match simple input/output token pricing within tolerance."
    return (
        "Reported CLI costs do not match simple input/output token pricing: "
        + ", ".join(mismatches)
        + ". Treat reported cost as Claude CLI telemetry, not raw API token billing."
    )


def format_live_comparison(rows: list[Metrics], records: list[dict], markdown: bool = False) -> str:
    provider = live_provider_summary(records)
    row_by_skill = {row.skill: row for row in rows}
    baseline_row = row_by_skill.get(DISPLAY["baseline"])
    baseline_provider = provider.get("baseline", {})
    headers = [
        "Skill",
        "Calls",
        "Est output tokens",
        "Est vs baseline",
        "Provider output tokens",
        "Provider vs baseline",
        "Cost USD",
        "Cost vs baseline",
        "Median latency ms",
        "Latency vs baseline",
        "Report overhead",
    ]
    body = []
    for arm in ROW_ORDER:
        row = row_by_skill.get(DISPLAY[arm])
        stats = provider.get(arm, {})
        provider_output = stats.get("provider_output_tokens") or 0
        cost = stats.get("cost_usd") or 0.0
        latency = stats.get("median_latency_ms") or 0.0
        body.append(
            [
                DISPLAY[arm],
                str(stats.get("calls", 0)),
                str(row.total_output_tokens if row else 0),
                pct_delta(row.total_output_tokens if row else 0, baseline_row.total_output_tokens if baseline_row else None),
                str(provider_output) if provider_output else "n/a",
                pct_delta(provider_output if provider_output else None, baseline_provider.get("provider_output_tokens")),
                f"{cost:.6f}" if cost else "n/a",
                pct_delta(cost if cost else None, baseline_provider.get("cost_usd")),
                f"{latency:g}" if latency else "n/a",
                pct_delta(latency if latency else None, baseline_provider.get("median_latency_ms")),
                f"{row.report_overhead:.1%}" if row else "0.0%",
            ]
        )
    if markdown:
        lines = ["| " + " | ".join(headers) + " |"]
        lines.append("|" + "|".join(["---"] * len(headers)) + "|")
        lines.extend("| " + " | ".join(row) + " |" for row in body)
        return "\n".join(lines)
    widths = [len(h) for h in headers]
    for row in body:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]
    lines = ["  ".join(cell.ljust(width) for cell, width in zip(headers, widths))]
    lines.append("  ".join("-" * width for width in widths))
    lines.extend("  ".join(cell.ljust(width) for cell, width in zip(row, widths)) for row in body)
    return "\n".join(lines)


def live_report_markdown(payload: dict) -> str:
    rows = [Metrics(**row) for row in payload.get("rows", [])]
    records = payload.get("records", [])
    warnings = payload.get("warnings", [])
    provider = live_provider_summary(records)
    input_price, output_price = pricing_from_payload(payload)
    def best_estimated() -> str:
        valid = [row for row in rows if row.total_output_tokens > 0]
        if not valid:
            return "n/a"
        row = min(valid, key=lambda item: item.total_output_tokens)
        return f"{row.skill} ({row.total_output_tokens} estimated visible tokens)"
    def best_provider_output() -> str:
        valid = [(arm, stats) for arm, stats in provider.items() if stats.get("provider_output_tokens")]
        if not valid:
            return "n/a"
        arm, stats = min(valid, key=lambda item: item[1]["provider_output_tokens"])
        return f"{DISPLAY[arm]} ({stats['provider_output_tokens']} provider output tokens)"
    def best_cost() -> str:
        valid = [(arm, stats) for arm, stats in provider.items() if stats.get("cost_usd")]
        if not valid:
            return "n/a"
        arm, stats = min(valid, key=lambda item: item[1]["cost_usd"])
        return f"{DISPLAY[arm]} (${stats['cost_usd']:.6f})"
    def best_latency() -> str:
        valid = [(arm, stats) for arm, stats in provider.items() if stats.get("median_latency_ms")]
        if not valid:
            return "n/a"
        arm, stats = min(valid, key=lambda item: item[1]["median_latency_ms"])
        return f"{DISPLAY[arm]} ({stats['median_latency_ms']:g} ms median)"
    lines = [
        "# Live Claude Benchmark",
        "",
        "Live model/API run. Do not compare these numbers to fixture results.",
        "",
        "## Metadata",
        "",
        f"- Provider: `{payload.get('provider', 'unknown')}`",
        f"- Model: `{payload.get('model', 'unknown')}`",
        f"- Runs: `{payload.get('runs', 'unknown')}`",
        f"- Generated: `{payload.get('generated_at', 'unknown')}`",
        "- Printed table estimated tokens use `ceil(UTF-8 bytes / 4)`.",
        "- Provider telemetry comes from Claude CLI JSON records when available.",
        f"- Simple API cost check uses `${input_price:g}`/MTok input and `${output_price:g}`/MTok output.",
        "",
        "## Highlights",
        "",
        f"- Shortest visible output: {best_estimated()}.",
        f"- Lowest provider output tokens: {best_provider_output()}.",
        f"- Lowest provider cost: {best_cost()}.",
        f"- Lowest median latency: {best_latency()}.",
        "",
        "## Comparison",
        "",
        format_live_comparison(rows, records, markdown=True),
        "",
        "## Provider Telemetry",
        "",
        format_live_telemetry(records, markdown=True),
        "",
        "## Cost Sanity Check",
        "",
        format_cost_sanity(records, markdown=True, input_price=input_price, output_price=output_price),
        "",
        cost_sanity_note(records, input_price=input_price, output_price=output_price),
        "",
        "## Interpretation",
        "",
        "- `Est output tokens` measures visible answer size using NoYap's deterministic heuristic.",
        "- `Provider output tokens` and `Cost USD` come from Claude CLI telemetry when present.",
        "- `Simple API cost USD` is input/output token math only.",
        "- Positive delta means lower than baseline; negative delta means higher than baseline.",
        "- NoYap is intended to reduce final-answer waste, not to minimize generated code LOC.",
        "",
    ]
    if warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)
        lines.append("")
    lines.extend(
        [
            "## External Inputs",
            "",
            "External comparison skill files were supplied by path at run time and are not vendored into NoYap.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_live_report(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(live_report_markdown(payload), encoding="utf-8")


def write_csv(rows: list[Metrics], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_json(rows: list[Metrics], warnings: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "mode": "fixture",
        "notice": "Fixture benchmark. Not live model/API usage.",
        "token_method": "ceil(UTF-8 bytes / 4), not provider-reported usage",
        "warnings": warnings,
        "rows": [asdict(row) for row in rows],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_live_json(rows: list[Metrics], records: list[dict], warnings: list[str], args: argparse.Namespace, path: Path) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "mode": "live",
        "provider": args.provider,
        "model": args.model,
        "runs": args.runs,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notice": "Live benchmark. Estimated table tokens are heuristic unless provider usage is present per record.",
        "token_method": "table uses ceil(UTF-8 bytes / 4); per-record usage may include provider-reported tokens",
        "pricing": {
            "input_usd_per_mtok": args.input_price_usd_per_mtok,
            "output_usd_per_mtok": args.output_price_usd_per_mtok,
            "note": "Used only for simple input/output API cost sanity checks. Provider-reported cost may include broader CLI telemetry.",
        },
        "external_skill_paths": {
            "caveman": str(args.caveman_skill) if args.caveman_skill else None,
            "ponytail": str(args.ponytail_skill) if args.ponytail_skill else None,
            "noyap": str(NOYAP_SKILL_PATH),
        },
        "warnings": warnings,
        "rows": [asdict(row) for row in rows],
        "records": records,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NoYap fixture benchmark")
    parser.add_argument("--mode", choices=("fixture", "live"), default="fixture")
    parser.add_argument("--provider", choices=("claude-cli",), default="claude-cli")
    parser.add_argument("--suite", choices=("coding", "final-report"), default="coding", help="task suite to run")
    parser.add_argument("--format", choices=("text", "markdown"), default="text")
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--report", type=Path, help="write Markdown report for live mode")
    parser.add_argument("--report-from-json", type=Path, help="write --report from an existing live JSON file")
    parser.add_argument("--runs", type=int, default=1, help="live runs per task per arm")
    parser.add_argument("--model", help="model name passed to the live provider")
    parser.add_argument("--timeout", type=int, default=180, help="seconds per live call")
    parser.add_argument("--input-price-usd-per-mtok", type=float, default=DEFAULT_INPUT_PRICE_USD_PER_MTOK, help="input token price used for simple live cost sanity checks")
    parser.add_argument("--output-price-usd-per-mtok", type=float, default=DEFAULT_OUTPUT_PRICE_USD_PER_MTOK, help="output token price used for simple live cost sanity checks")
    parser.add_argument("--caveman-skill", type=Path, help="path to external Caveman SKILL.md")
    parser.add_argument("--ponytail-skill", type=Path, help="path to external Ponytail SKILL.md")
    args = parser.parse_args(argv)

    if args.report_from_json:
        if not args.report:
            print("error: --report is required with --report-from-json", file=sys.stderr)
            return 1
        try:
            payload = json.loads(args.report_from_json.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"error: cannot read report JSON: {exc}", file=sys.stderr)
            return 1
        write_live_report(payload, args.report)
        print(f"Wrote {args.report}")
        return 0

    try:
        tasks = load_tasks(task_path_for_suite(args.suite))
        if args.mode == "fixture":
            rows, warnings = run_fixture(tasks)
            records = None
        else:
            rows, records, warnings = run_live_claude_cli(
                tasks=tasks,
                runs=args.runs,
                model=args.model,
                timeout=args.timeout,
                caveman_skill=args.caveman_skill,
                ponytail_skill=args.ponytail_skill,
            )
    except BenchmarkError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired as exc:
        print(f"error: live provider timed out after {exc.timeout}s", file=sys.stderr)
        return 1

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    if args.mode == "fixture":
        print("Fixture benchmark. Not live model/API usage.")
        print("Estimated tokens: ceil(UTF-8 bytes / 4), not provider-reported usage.")
    else:
        print("Live benchmark via claude-cli.")
        print("Table tokens are estimated with ceil(UTF-8 bytes / 4); provider usage is stored in JSON records when available.")
    print()
    if args.mode == "live":
        print(format_live_comparison(rows, records or [], markdown=args.format == "markdown"))
    else:
        print(format_table(rows, markdown=args.format == "markdown"))
    if args.mode == "live":
        print()
        print(format_live_telemetry(records or [], markdown=args.format == "markdown"))
        print()
        print(format_cost_sanity(records or [], markdown=args.format == "markdown", input_price=args.input_price_usd_per_mtok, output_price=args.output_price_usd_per_mtok))

    if args.csv:
        write_csv(rows, args.csv)
    if args.json:
        if args.mode == "fixture":
            write_json(rows, warnings, args.json)
        else:
            payload = write_live_json(rows, records or [], warnings, args, args.json)
            if args.report:
                write_live_report(payload, args.report)
    elif args.mode == "live" and args.report:
        payload = {
            "mode": "live",
            "provider": args.provider,
            "model": args.model,
            "runs": args.runs,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pricing": {
                "input_usd_per_mtok": args.input_price_usd_per_mtok,
                "output_usd_per_mtok": args.output_price_usd_per_mtok,
                "note": "Used only for simple input/output API cost sanity checks. Provider-reported cost may include broader CLI telemetry.",
            },
            "warnings": warnings,
            "rows": [asdict(row) for row in rows],
            "records": records or [],
        }
        write_live_report(payload, args.report)
    if args.mode == "live" and warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
