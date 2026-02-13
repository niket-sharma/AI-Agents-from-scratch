from __future__ import annotations

from pathlib import Path
from typing import List

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.llm_client import LLMClient
from shared.metrics import evaluate_quality, extract_citations
from shared.schemas import RetrievedChunk, RunResult
from shared.vector_store import LocalVectorStore


class BasicRAGPipeline:
    def __init__(self, store: LocalVectorStore, llm_client: LLMClient, top_k: int = 5) -> None:
        self.store = store
        self.llm_client = llm_client
        self.top_k = top_k

    def _format_excerpts(self, retrieved: List[RetrievedChunk]) -> str:
        lines: List[str] = []
        for item in retrieved:
            lines.append(
                f"[{item.chunk.doc_name}|{item.chunk.chunk_id}] "
                f"(section: {item.chunk.section}, score={item.score:.3f})\n{item.chunk.text}"
            )
        return "\n\n".join(lines)

    def run(
        self,
        query_id: str,
        query_text: str,
        expected_numeric: float | None = None,
        tolerance: float = 0.01,
    ) -> RunResult:
        retrieved = self.store.search(query_text, top_k=self.top_k)
        retrieved_chunk_ids = [r.chunk.chunk_id for r in retrieved]

        system_prompt = (
            "You are a policy QA assistant. Answer using only the provided policy excerpts. "
            "Cite every important claim as [doc|chunk_id]. If unsupported, say you do not have enough policy context."
        )
        user_prompt = (
            f"Question:\n{query_text}\n\n"
            f"Policy excerpts:\n{self._format_excerpts(retrieved)}\n\n"
            "Return a concise answer with citations."
        )

        llm_response = self.llm_client.call_llm(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            call_name="basic_rag_answer",
        )

        answer = llm_response["text"]
        citations = extract_citations(answer)

        result = RunResult(
            query_id=query_id,
            query_text=query_text,
            workflow_type="basic",
            num_llm_calls=1,
            llm_calls=[llm_response["record"]],
            total_prompt_tokens=llm_response["usage"].prompt_tokens,
            total_completion_tokens=llm_response["usage"].completion_tokens,
            total_tokens=llm_response["usage"].total_tokens,
            latency_ms_total=llm_response["latency_ms"],
            citations_used=citations,
            retrieved_chunk_ids=retrieved_chunk_ids,
            final_answer=answer,
        )

        result.quality_checks = evaluate_quality(
            answer=answer,
            citations=citations,
            retrieved_chunk_ids=retrieved_chunk_ids,
            expected_numeric=expected_numeric,
            tolerance=tolerance,
            validator_status=None,
        )
        return result
