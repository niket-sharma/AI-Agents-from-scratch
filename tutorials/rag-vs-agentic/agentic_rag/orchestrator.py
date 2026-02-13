from __future__ import annotations

from pathlib import Path
from typing import List

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_rag.agents.finalizer import FinalizerAgent
from agentic_rag.agents.planner import PlannerAgent
from agentic_rag.agents.reasoner import ReasonerAgent
from agentic_rag.agents.retriever import RetrieverAgent
from agentic_rag.agents.validator import ValidatorAgent
from agentic_rag.tools.calculator import evaluate_expression
from shared.llm_client import LLMClient
from shared.metrics import evaluate_quality, extract_citations
from shared.schemas import LLMCallRecord, RetrievedChunk, RunResult
from shared.vector_store import LocalVectorStore


class AgenticRAGOrchestrator:
    def __init__(
        self,
        store: LocalVectorStore,
        llm_client: LLMClient,
        max_steps: int = 4,
        max_retrieval_retries: int = 1,
        use_finalizer: bool = True,
    ) -> None:
        self.store = store
        self.max_steps = max_steps
        self.max_retrieval_retries = max_retrieval_retries
        self.use_finalizer = use_finalizer

        self.planner = PlannerAgent(llm_client)
        self.retriever = RetrieverAgent(store=store)
        self.reasoner = ReasonerAgent(llm_client)
        self.validator = ValidatorAgent(llm_client)
        self.finalizer = FinalizerAgent(llm_client)

    def _accumulate(self, calls: List[LLMCallRecord]) -> tuple[int, int, int, int]:
        prompt = sum(c.usage.prompt_tokens for c in calls)
        completion = sum(c.usage.completion_tokens for c in calls)
        total = sum(c.usage.total_tokens for c in calls)
        latency = sum(c.latency_ms for c in calls)
        return prompt, completion, total, latency

    def run(
        self,
        query_id: str,
        query_text: str,
        expected_numeric: float | None = None,
        tolerance: float = 0.01,
    ) -> RunResult:
        llm_calls: List[LLMCallRecord] = []

        plan = self.planner.plan(query_text)
        llm_calls.append(plan["_llm"]["record"])

        retrieved = self.retriever.retrieve(plan=plan, fallback_query=query_text)
        retrieved_map = {r.chunk.chunk_id: r for r in retrieved}

        tool_note = None
        if bool(plan.get("needs_calculation")) and str(plan.get("calculation_expression") or "").strip():
            expr = str(plan.get("calculation_expression")).strip()
            try:
                value = evaluate_expression(expr)
                tool_note = f"calculator({expr}) = {value}"
            except Exception as exc:
                tool_note = f"calculator_error: {exc}"

        reason = self.reasoner.reason(
            question=query_text,
            plan=plan,
            retrieved=list(retrieved_map.values()),
            tool_result=tool_note,
        )
        llm_calls.append(reason["_llm"]["record"])

        validator = self.validator.validate(
            question=query_text,
            draft_answer=reason.get("draft_answer", ""),
            claims=reason.get("claims", []),
            retrieved=list(retrieved_map.values()),
        )
        llm_calls.append(validator["_llm"]["record"])

        retries = 0
        while (
            validator.get("status") == "needs_more_context"
            and retries < self.max_retrieval_retries
            and len(llm_calls) < self.max_steps
        ):
            refined_query = validator.get("refined_query") or query_text
            extra = self.store.search(refined_query, top_k=4)
            for item in extra:
                existing = retrieved_map.get(item.chunk.chunk_id)
                if existing is None or item.score > existing.score:
                    retrieved_map[item.chunk.chunk_id] = item

            if len(llm_calls) >= self.max_steps:
                break

            reason = self.reasoner.reason(
                question=query_text,
                plan=plan,
                retrieved=list(retrieved_map.values()),
                tool_result=tool_note,
            )
            llm_calls.append(reason["_llm"]["record"])

            if len(llm_calls) >= self.max_steps:
                break

            validator = self.validator.validate(
                question=query_text,
                draft_answer=reason.get("draft_answer", ""),
                claims=reason.get("claims", []),
                retrieved=list(retrieved_map.values()),
            )
            llm_calls.append(validator["_llm"]["record"])
            retries += 1

        final_answer = reason.get("draft_answer", "")
        if self.use_finalizer and len(llm_calls) < self.max_steps:
            final = self.finalizer.finalize(
                question=query_text,
                draft_answer=reason.get("draft_answer", ""),
                claims=reason.get("claims", []),
                validator_issues=validator.get("issues", []),
            )
            llm_calls.append(final["_llm"]["record"])
            final_answer = final["text"]

        citations = extract_citations(final_answer)
        retrieved_chunk_ids = list(retrieved_map.keys())

        prompt_t, completion_t, total_t, latency = self._accumulate(llm_calls)
        result = RunResult(
            query_id=query_id,
            query_text=query_text,
            workflow_type="agentic",
            num_llm_calls=len(llm_calls),
            llm_calls=llm_calls,
            total_prompt_tokens=prompt_t,
            total_completion_tokens=completion_t,
            total_tokens=total_t,
            latency_ms_total=latency,
            citations_used=citations,
            retrieved_chunk_ids=retrieved_chunk_ids,
            final_answer=final_answer,
            validator_status=validator.get("status"),
            validator_notes="; ".join(validator.get("issues", [])) if validator.get("issues") else "",
        )
        result.quality_checks = evaluate_quality(
            answer=final_answer,
            citations=citations,
            retrieved_chunk_ids=retrieved_chunk_ids,
            expected_numeric=expected_numeric,
            tolerance=tolerance,
            validator_status=result.validator_status,
        )
        return result
