from __future__ import annotations

from typing import List, Optional

import chromadb

from src.memory.base import BaseMemory
from src.utils.messages import Message


class EpisodicMemory(BaseMemory):
    """
    Stores conversation turns in a local vector store (ChromaDB) and retrieves
    the most semantically relevant episodes for the current context.

    Persists to disk — survives process restarts (cross-session memory).
    """

    def __init__(
        self,
        collection_name: str = "episodes",
        persist_dir: str = "./.episodic_memory",
        top_k: int = 5,
    ) -> None:
        super().__init__()
        self._top_k = top_k
        self._chroma = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._chroma.get_or_create_collection(collection_name)
        # Pick up where a prior session left off
        self._id_counter: int = self._collection.count()

    def add(self, message: Message) -> None:
        super().add(message)
        self._collection.add(
            documents=[message.content],
            metadatas=[{"role": message.role}],
            ids=[str(self._id_counter)],
        )
        self._id_counter += 1

    def get_context(self) -> List[Message]:
        count = self._collection.count()
        if count == 0:
            return []

        user_messages = [m for m in self._messages if m.role == "user"]

        if user_messages:
            # Semantic retrieval: find episodes most relevant to the latest user turn
            query = user_messages[-1].content
            n = min(self._top_k, count)
            results = self._collection.query(query_texts=[query], n_results=n)
            docs: List[str] = results["documents"][0]
            metas: List[dict] = results["metadatas"][0]
            return [Message(role=meta["role"], content=doc) for doc, meta in zip(docs, metas)]
        else:
            # Fresh session with no in-memory messages — return the most recent K episodes
            start = max(0, self._id_counter - self._top_k)
            ids = [str(i) for i in range(start, self._id_counter)]
            if not ids:
                return []
            result = self._collection.get(ids=ids, include=["documents", "metadatas"])
            return [
                Message(role=meta["role"], content=doc)
                for doc, meta in zip(result["documents"], result["metadatas"])
            ]

    def reset(self) -> None:
        super().reset()
        self._chroma.delete_collection(self._collection.name)
        self._collection = self._chroma.get_or_create_collection(self._collection.name)
        self._id_counter = 0
