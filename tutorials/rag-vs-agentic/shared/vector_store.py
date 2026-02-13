from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from shared.embeddings import cosine_similarity, embed_text
from shared.schemas import Chunk, RetrievedChunk


class LocalVectorStore:
    def __init__(self) -> None:
        self._chunks: Dict[str, Chunk] = {}
        self._vectors: Dict[str, dict] = {}

    def add_chunks(self, chunks: Iterable[Chunk]) -> None:
        for chunk in chunks:
            self._chunks[chunk.chunk_id] = chunk
            self._vectors[chunk.chunk_id] = embed_text(chunk.text)

    def get_chunk(self, chunk_id: str) -> Optional[Chunk]:
        return self._chunks.get(chunk_id)

    def search(
        self,
        query: str,
        top_k: int = 5,
        allowed_docs: Optional[set[str]] = None,
    ) -> List[RetrievedChunk]:
        qv = embed_text(query)
        scored: List[RetrievedChunk] = []

        for chunk_id, chunk in self._chunks.items():
            if allowed_docs and chunk.doc_name not in allowed_docs:
                continue
            score = cosine_similarity(qv, self._vectors[chunk_id])
            if score > 0:
                scored.append(RetrievedChunk(chunk=chunk, score=score))

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]
