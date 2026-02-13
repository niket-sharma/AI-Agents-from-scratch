from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.metrics import summarize_runs


def load_records(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def find_latest_result(results_dir: Path) -> Path:
    files = sorted(results_dir.glob("run_*.jsonl"))
    if not files:
        raise FileNotFoundError("No run_*.jsonl files found in experiments/results")
    return files[-1]


def print_markdown_table(basic: dict, agentic: dict) -> None:
    headers = [
        "Metric",
        "Basic RAG",
        "Agentic RAG",
    ]
    rows = [
        ("Runs", basic.get("count", 0), agentic.get("count", 0)),
        ("Avg Total Tokens", basic.get("avg_total_tokens", 0), agentic.get("avg_total_tokens", 0)),
        ("Median Total Tokens", basic.get("median_total_tokens", 0), agentic.get("median_total_tokens", 0)),
        ("Avg Prompt Tokens", basic.get("avg_prompt_tokens", 0), agentic.get("avg_prompt_tokens", 0)),
        (
            "Avg Completion Tokens",
            basic.get("avg_completion_tokens", 0),
            agentic.get("avg_completion_tokens", 0),
        ),
        ("Avg Latency (ms)", basic.get("avg_latency_ms", 0), agentic.get("avg_latency_ms", 0)),
        ("Median Latency (ms)", basic.get("median_latency_ms", 0), agentic.get("median_latency_ms", 0)),
        ("Avg # LLM Calls", basic.get("avg_llm_calls", 0), agentic.get("avg_llm_calls", 0)),
        ("Failure Rate", basic.get("failure_rate", 0), agentic.get("failure_rate", 0)),
        ("Task Accuracy", basic.get("task_accuracy", 0), agentic.get("task_accuracy", 0)),
        (
            "Tokens / Correct Answer",
            basic.get("tokens_per_correct_answer", 0),
            agentic.get("tokens_per_correct_answer", 0),
        ),
        (
            "Avg Quality Proxy",
            basic.get("avg_quality_proxy_score", 0),
            agentic.get("avg_quality_proxy_score", 0),
        ),
    ]

    print("| " + " | ".join(headers) + " |")
    print("|---|---:|---:|")
    for row in rows:
        print(f"| {row[0]} | {row[1]} | {row[2]} |")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze benchmark JSONL outputs")
    parser.add_argument("--file", default="", help="Path to run JSONL file. If omitted, latest is used.")
    args = parser.parse_args()

    results_dir = PROJECT_ROOT / "experiments" / "results"
    path = Path(args.file) if args.file else find_latest_result(results_dir)
    rows = load_records(path)

    basic_rows = [r for r in rows if r["workflow_type"] == "basic"]
    agentic_rows = [r for r in rows if r["workflow_type"] != "basic"]

    basic = summarize_runs(basic_rows)
    agentic = summarize_runs(agentic_rows)

    print(f"Using results file: {path}")
    print()
    print_markdown_table(basic, agentic)


if __name__ == "__main__":
    main()
