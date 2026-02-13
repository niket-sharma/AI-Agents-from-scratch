from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from basic_rag.pipeline import BasicRAGPipeline
from shared.chunking import load_policy_chunks
from shared.llm_client import LLMClient
from shared.metrics import evaluate_quality, summarize_runs
from shared.schemas import BenchmarkQuestion
from shared.vector_store import LocalVectorStore


def load_questions(path: Path) -> list[BenchmarkQuestion]:
    rows: list[BenchmarkQuestion] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        rows.append(
            BenchmarkQuestion(
                query_id=obj["query_id"],
                query_text=obj["query_text"],
                expected_numeric=obj.get("expected_numeric"),
                tolerance=obj.get("tolerance", 0.01),
                expected_keywords_any=obj.get("expected_keywords_any", []),
                expected_keywords_all=obj.get("expected_keywords_all", []),
                forbidden_keywords=obj.get("forbidden_keywords", []),
            )
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Run basic vs agentic RAG benchmark")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model name")
    parser.add_argument("--top-k", type=int, default=5, help="Top-k retrieval for basic pipeline")
    parser.add_argument("--limit", type=int, default=0, help="Optional question limit")
    parser.add_argument(
        "--agentic-backend",
        choices=["custom", "openai_sdk"],
        default="custom",
        help="Agentic implementation backend",
    )
    args = parser.parse_args()

    data_dir = PROJECT_ROOT / "data"
    output_dir = PROJECT_ROOT / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    questions = load_questions(data_dir / "benchmark_questions.jsonl")
    if args.limit > 0:
        questions = questions[: args.limit]

    chunks = load_policy_chunks(data_dir=data_dir)
    store = LocalVectorStore()
    store.add_chunks(chunks)

    llm_client = LLMClient(model=args.model, temperature=0.0)
    basic = BasicRAGPipeline(store=store, llm_client=llm_client, top_k=args.top_k)
    if args.agentic_backend == "custom":
        from agentic_rag.orchestrator import AgenticRAGOrchestrator

        agentic = AgenticRAGOrchestrator(store=store, llm_client=llm_client)
    else:
        from agentic_rag_openai_sdk.orchestrator import OpenAIAgentsSDKOrchestrator

        agentic = OpenAIAgentsSDKOrchestrator(store=store, model=args.model)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"run_{ts}.jsonl"

    records = []
    with output_path.open("w", encoding="utf-8") as f:
        for q in questions:
            basic_res = basic.run(
                query_id=q.query_id,
                query_text=q.query_text,
                expected_numeric=q.expected_numeric,
                tolerance=q.tolerance,
            )
            basic_res.quality_checks = evaluate_quality(
                answer=basic_res.final_answer,
                citations=basic_res.citations_used,
                retrieved_chunk_ids=basic_res.retrieved_chunk_ids,
                expected_numeric=q.expected_numeric,
                tolerance=q.tolerance,
                validator_status=basic_res.validator_status,
                expected_keywords_any=q.expected_keywords_any,
                expected_keywords_all=q.expected_keywords_all,
                forbidden_keywords=q.forbidden_keywords,
            )
            basic_obj = basic_res.to_json_dict()
            f.write(json.dumps(basic_obj) + "\n")
            records.append(basic_obj)

            agentic_res = agentic.run(
                query_id=q.query_id,
                query_text=q.query_text,
                expected_numeric=q.expected_numeric,
                tolerance=q.tolerance,
            )
            agentic_res.quality_checks = evaluate_quality(
                answer=agentic_res.final_answer,
                citations=agentic_res.citations_used,
                retrieved_chunk_ids=agentic_res.retrieved_chunk_ids,
                expected_numeric=q.expected_numeric,
                tolerance=q.tolerance,
                validator_status=agentic_res.validator_status,
                expected_keywords_any=q.expected_keywords_any,
                expected_keywords_all=q.expected_keywords_all,
                forbidden_keywords=q.forbidden_keywords,
            )
            agentic_obj = agentic_res.to_json_dict()
            f.write(json.dumps(agentic_obj) + "\n")
            records.append(agentic_obj)

    basic_rows = [r for r in records if r["workflow_type"] == "basic"]
    agentic_rows = [r for r in records if r["workflow_type"] != "basic"]

    print(f"Saved run file: {output_path}")
    print("\nSummary")
    print("basic  :", summarize_runs(basic_rows))
    print("agentic:", summarize_runs(agentic_rows))


if __name__ == "__main__":
    main()
