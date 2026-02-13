from __future__ import annotations

from typing import Any, Dict, List

from shared.schemas import RetrievedChunk
from shared.vector_store import LocalVectorStore


class RetrieverAgent:
    def __init__(self, store: LocalVectorStore, top_k_per_query: int = 4) -> None:
        self.store = store
        self.top_k_per_query = top_k_per_query

    def retrieve(self, plan: Dict[str, Any], fallback_query: str) -> List[RetrievedChunk]:
        queries = plan.get("retrieval_queries") or [fallback_query]
        target_docs = set(plan.get("target_docs") or [])
        allowed_docs = target_docs if target_docs else None

        merged: dict[str, RetrievedChunk] = {}
        for q in queries:
            results = self.store.search(
                query=q,
                top_k=self.top_k_per_query,
                allowed_docs=allowed_docs,
            )
            for r in results:
                current = merged.get(r.chunk.chunk_id)
                if current is None or r.score > current.score:
                    merged[r.chunk.chunk_id] = r

        ordered = sorted(merged.values(), key=lambda x: x.score, reverse=True)
        return ordered
