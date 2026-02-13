from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Literal, Optional

import sys

from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.metrics import evaluate_quality, extract_citations
from shared.schemas import LLMCallRecord, LLMUsage, RunResult
from shared.vector_store import LocalVectorStore


@dataclass
class AgenticContext:
    store: LocalVectorStore
    default_top_k: int = 4


class PlannerOutput(BaseModel):
    subquestions: List[str] = Field(default_factory=list)
    retrieval_queries: List[str] = Field(default_factory=list)
    target_docs: List[str] = Field(default_factory=list)
    needs_calculation: bool = False
    calculation_expression: str = ""
    reasoning_notes: str = ""


class Claim(BaseModel):
    text: str
    citation_ids: List[str] = Field(default_factory=list)


class ReasonerOutput(BaseModel):
    draft_answer: str
    claims: List[Claim] = Field(default_factory=list)


class ValidatorOutput(BaseModel):
    status: Literal["pass", "needs_more_context"] = "pass"
    issues: List[str] = Field(default_factory=list)
    refined_query: str = ""


class OpenAIAgentsSDKOrchestrator:
    def __init__(
        self,
        store: LocalVectorStore,
        model: str = "gpt-4o-mini",
        max_steps: int = 8,
        max_retrieval_retries: int = 1,
    ) -> None:
        self.store = store
        self.model = model
        self.max_steps = max_steps
        self.max_retrieval_retries = max_retrieval_retries

        try:
            from agents import Agent, Runner, RunContextWrapper, function_tool
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "OpenAI Agents SDK is required for this backend. Install with: pip install openai-agents"
            ) from exc

        self.Runner = Runner
        self.context = AgenticContext(store=store)

        @function_tool
        def retrieve_policy_chunks(
            ctx: RunContextWrapper[AgenticContext],
            query: str,
            top_k: int = 4,
            target_docs: Optional[List[str]] = None,
        ) -> str:
            allowed_docs = set(target_docs) if target_docs else None
            results = ctx.context.store.search(query=query, top_k=top_k, allowed_docs=allowed_docs)
            payload = []
            for item in results:
                payload.append(
                    {
                        "doc": item.chunk.doc_name,
                        "chunk_id": item.chunk.chunk_id,
                        "section": item.chunk.section,
                        "score": round(item.score, 4),
                        "text": item.chunk.text,
                    }
                )
            return json.dumps(payload)

        @function_tool
        def calculator(expression: str) -> str:
            from agentic_rag.tools.calculator import evaluate_expression

            value = evaluate_expression(expression)
            return json.dumps({"expression": expression, "value": value})

        planner_instructions = (
            "You are a planner for policy QA. Produce a structured plan only. "
            "Keep retrieval_queries specific and include target_docs when clear."
        )
        reasoner_instructions = (
            "You are a policy reasoner. Use tools to retrieve policy chunks before answering. "
            "Ground claims in retrieved chunks and include citation ids in claims."
        )
        validator_instructions = (
            "You validate whether claims are supported by cited chunk ids. "
            "If support is weak, return needs_more_context with a refined retrieval query."
        )

        self.planner_agent = Agent(
            name="planner",
            model=self.model,
            instructions=planner_instructions,
            output_type=PlannerOutput,
        )
        self.reasoner_agent = Agent(
            name="reasoner",
            model=self.model,
            instructions=reasoner_instructions,
            tools=[retrieve_policy_chunks, calculator],
            output_type=ReasonerOutput,
        )
        self.validator_agent = Agent(
            name="validator",
            model=self.model,
            instructions=validator_instructions,
            output_type=ValidatorOutput,
        )

    def _run_agent(self, agent: Any, prompt: str, call_name: str) -> tuple[Any, List[LLMCallRecord]]:
        start = time.perf_counter()
        result = self.Runner.run_sync(
            starting_agent=agent,
            input=prompt,
            context=self.context,
            max_turns=self.max_steps,
        )
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        records = self._extract_usage_records(result=result, call_name=call_name, elapsed_ms=elapsed_ms)
        return result, records

    def _extract_usage_records(self, result: Any, call_name: str, elapsed_ms: int) -> List[LLMCallRecord]:
        usage = getattr(getattr(result, "context_wrapper", None), "usage", None)
        entries = list(getattr(usage, "request_usage_entries", []) or [])

        records: List[LLMCallRecord] = []
        if entries:
            per_call_latency = max(1, elapsed_ms // len(entries))
            for idx, entry in enumerate(entries, start=1):
                prompt_tokens = int(getattr(entry, "input_tokens", 0) or 0)
                completion_tokens = int(getattr(entry, "output_tokens", 0) or 0)
                total_tokens = int(getattr(entry, "total_tokens", prompt_tokens + completion_tokens) or 0)
                model = str(getattr(entry, "model", self.model) or self.model)

                records.append(
                    LLMCallRecord(
                        call_name=f"{call_name}_{idx}",
                        model=model,
                        latency_ms=per_call_latency,
                        usage=LLMUsage(
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            total_tokens=total_tokens,
                        ),
                        prompt_preview="(Agents SDK request)",
                    )
                )
            return records

        prompt_tokens = int(getattr(usage, "input_tokens", 0) or 0) if usage is not None else 0
        completion_tokens = int(getattr(usage, "output_tokens", 0) or 0) if usage is not None else 0
        total_tokens = int(getattr(usage, "total_tokens", prompt_tokens + completion_tokens) or 0) if usage is not None else 0

        records.append(
            LLMCallRecord(
                call_name=call_name,
                model=self.model,
                latency_ms=elapsed_ms,
                usage=LLMUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                ),
                prompt_preview="(Agents SDK request)",
            )
        )
        return records

    def run(
        self,
        query_id: str,
        query_text: str,
        expected_numeric: Optional[float] = None,
        tolerance: float = 0.01,
    ) -> RunResult:
        llm_calls: List[LLMCallRecord] = []

        planner_prompt = (
            "Question:\n"
            f"{query_text}\n\n"
            "Allowed docs: expense_policy, travel_policy, remote_work, procurement, faq."
        )
        planner_result, planner_records = self._run_agent(
            agent=self.planner_agent,
            prompt=planner_prompt,
            call_name="planner",
        )
        llm_calls.extend(planner_records)
        plan: PlannerOutput = planner_result.final_output

        reason_prompt = (
            f"Question: {query_text}\n\n"
            f"Plan JSON: {plan.model_dump_json()}\n\n"
            "Use retrieve_policy_chunks for each retrieval query and target docs. "
            "If numeric computation is required, use calculator tool."
        )
        reason_result, reason_records = self._run_agent(
            agent=self.reasoner_agent,
            prompt=reason_prompt,
            call_name="reasoner",
        )
        llm_calls.extend(reason_records)
        draft: ReasonerOutput = reason_result.final_output

        validator_prompt = (
            f"Question: {query_text}\n\n"
            f"Plan: {plan.model_dump_json()}\n\n"
            f"Draft: {draft.model_dump_json()}\n\n"
            "Check support and citation alignment."
        )
        validator_result, validator_records = self._run_agent(
            agent=self.validator_agent,
            prompt=validator_prompt,
            call_name="validator",
        )
        llm_calls.extend(validator_records)
        validator: ValidatorOutput = validator_result.final_output

        retries = 0
        while validator.status == "needs_more_context" and retries < self.max_retrieval_retries:
            retry_prompt = (
                f"Question: {query_text}\n\n"
                f"Plan JSON: {plan.model_dump_json()}\n\n"
                f"Validator refined query: {validator.refined_query}\n\n"
                "Run additional retrieval with this query, then produce improved draft answer and claims."
            )
            reason_result, reason_records = self._run_agent(
                agent=self.reasoner_agent,
                prompt=retry_prompt,
                call_name=f"reasoner_retry_{retries + 1}",
            )
            llm_calls.extend(reason_records)
            draft = reason_result.final_output

            validator_prompt = (
                f"Question: {query_text}\n\n"
                f"Plan: {plan.model_dump_json()}\n\n"
                f"Updated draft: {draft.model_dump_json()}\n\n"
                "Check support and citation alignment."
            )
            validator_result, validator_records = self._run_agent(
                agent=self.validator_agent,
                prompt=validator_prompt,
                call_name=f"validator_retry_{retries + 1}",
            )
            llm_calls.extend(validator_records)
            validator = validator_result.final_output
            retries += 1

        final_answer = draft.draft_answer
        citations = extract_citations(final_answer)

        prompt_total = sum(c.usage.prompt_tokens for c in llm_calls)
        completion_total = sum(c.usage.completion_tokens for c in llm_calls)
        token_total = sum(c.usage.total_tokens for c in llm_calls)
        latency_total = sum(c.latency_ms for c in llm_calls)

        result = RunResult(
            query_id=query_id,
            query_text=query_text,
            workflow_type="agentic_openai_sdk",
            num_llm_calls=len(llm_calls),
            llm_calls=llm_calls,
            total_prompt_tokens=prompt_total,
            total_completion_tokens=completion_total,
            total_tokens=token_total,
            latency_ms_total=latency_total,
            citations_used=citations,
            retrieved_chunk_ids=[c["chunk_id"] for c in citations],
            final_answer=final_answer,
            validator_status=validator.status,
            validator_notes="; ".join(validator.issues),
        )
        result.quality_checks = evaluate_quality(
            answer=final_answer,
            citations=citations,
            retrieved_chunk_ids=result.retrieved_chunk_ids,
            expected_numeric=expected_numeric,
            tolerance=tolerance,
            validator_status=result.validator_status,
        )
        return result
