# RAG vs Agentic RAG: Company Policy QA Benchmark

This tutorial implements the same QA app in two styles and compares token, latency, and quality proxy metrics.
It is designed as an extensible benchmark harness, not a from-scratch-only pattern.

## What You Build

- Basic RAG: single retrieval + single LLM call answer.
- Agentic RAG: planner, retriever, reasoner, optional calculator, validator, and optional finalizer with multiple LLM calls.
- Benchmark harness that runs both workflows over a fixed question set and logs per-call API usage.

Application domain: company policy QA for expense, travel, remote work, and procurement.

## Project Layout

```

`shared/` here means reusable components across both workflows. You can swap internals (embeddings, vector DB, orchestrator) without changing the benchmark contract.
rag-vs-agentic/
  README.md
  data/
    policies/*.md
    benchmark_questions.jsonl
  shared/
    chunking.py
    embeddings.py
    vector_store.py
    llm_client.py
    metrics.py
    schemas.py
  basic_rag/
    pipeline.py
  agentic_rag/
    agents/
      planner.py
      retriever.py
      reasoner.py
      validator.py
      finalizer.py
    orchestrator.py
    tools/
      calculator.py
  experiments/
    run_benchmark.py
    analyze_results.py
    results/*.jsonl
```

## Setup

1. Ensure dependencies are installed from repo root:
   - `pip install -r requirements.txt`
2. Optional (for OpenAI Agents SDK backend):
   - `pip install openai-agents`
3. Set API key:
   - `export OPENAI_API_KEY=...`

## Run Benchmark

From `tutorials/rag-vs-agentic`:

```bash
python experiments/run_benchmark.py --model gpt-4o-mini
```

Optional:

```bash
python experiments/run_benchmark.py --model gpt-4o-mini --limit 10 --top-k 5
```

Use OpenAI Agents SDK backend:

```bash
python experiments/run_benchmark.py --model gpt-4o-mini --agentic-backend openai_sdk
```

Results are written to:

- `experiments/results/run_<timestamp>.jsonl`

Each JSONL row includes:

- `query_id`, `query_text`
- `workflow_type` (`basic`, `agentic`, or `agentic_openai_sdk`)
- `num_llm_calls`
- per-call usage (`prompt_tokens`, `completion_tokens`, `total_tokens`)
- per-call latency and total latency
- retrieved chunk ids and extracted citations
- final answer
- quality checks

`quality_checks` now includes:
- citation and validator checks (quality proxy)
- numeric correctness (when `expected_numeric` is present)
- keyword-based task correctness for non-numeric questions
- `task_correct` boolean used for benchmark accuracy summaries

## Analyze Results

```bash
python experiments/analyze_results.py
```

Or pass a specific file:

```bash
python experiments/analyze_results.py --file experiments/results/run_YYYYMMDD_HHMMSS.jsonl
```

This prints a markdown comparison table across both workflows.
The table includes task accuracy and tokens-per-correct-answer in addition to token and latency metrics.

## Cost/Token Tradeoff

Expected behavior:

- Basic RAG is cheaper and faster (fewer tokens, 1 call).
- Agentic RAG is more expensive (2 to 4 calls) but can be more robust on multi-hop and numeric questions due to planning + validation.

In general, use agentic flow when:

- questions are multi-step or cross-document,
- strict citation checks matter,
- numeric consistency matters.

Use basic flow when:

- throughput and low latency dominate,
- questions are short and single-hop,
- lightweight quality guarantees are acceptable.

## Extending Beyond This Baseline

You can plug in other stacks while keeping the same benchmark outputs:

- Retrieval upgrades:
  - Replace `shared/vector_store.py` with FAISS or Chroma.
  - Replace `shared/embeddings.py` with model embeddings (for example OpenAI embeddings).
- Agentic orchestration upgrades:
  - Keep current custom orchestrator, or swap to frameworks like LangGraph, LlamaIndex workflows, CrewAI, or AutoGen.
- Evaluation continuity:
  - Keep `experiments/run_benchmark.py` output schema stable so comparisons remain apples-to-apples.

## Notes

- Token accounting uses the OpenAI API `usage` object fields: `prompt_tokens`, `completion_tokens`, `total_tokens`.
- Benchmark uses non-streaming calls to ensure usage metrics are captured.
