"""
Lightweight retrieval-augmented generation example.
"""

from __future__ import annotations

from collections import Counter
from math import sqrt
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import BaseAgent
from src.memory import ConversationBufferMemory


def _tokenize(text: str) -> List[str]:
    return [token.lower() for token in text.split() if token.strip()]


class InMemoryVectorStore:
    """Very small vector store for tutorial purposes."""

    def __init__(self) -> None:
        self._documents: Dict[str, str] = {}
        self._vectors: Dict[str, Counter[str]] = {}

    def add_document(self, doc_id: str, text: str) -> None:
        self._documents[doc_id] = text
        self._vectors[doc_id] = Counter(_tokenize(text))

    def add_directory(self, path: Path, pattern: str = "*.md") -> None:
        for file_path in path.rglob(pattern):
            self.add_document(file_path.stem, file_path.read_text(encoding="utf-8"))

    def list_ids(self) -> List[str]:
        return list(self._documents.keys())

    def similarity(self, vector_a: Counter[str], vector_b: Counter[str]) -> float:
        numerator = sum(vector_a[token] * vector_b[token] for token in vector_a)
        if not numerator:
            return 0.0
        norm_a = sqrt(sum(value * value for value in vector_a.values()))
        norm_b = sqrt(sum(value * value for value in vector_b.values()))
        if not norm_a or not norm_b:
            return 0.0
        return numerator / (norm_a * norm_b)

    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float, str]]:
        query_vector = Counter(_tokenize(query))
        scored: List[Tuple[str, float, str]] = []
        for doc_id, vector in self._vectors.items():
            score = self.similarity(query_vector, vector)
            if score > 0:
                scored.append((doc_id, score, self._documents[doc_id]))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]


class RAGAgent:
    """Wraps a BaseAgent to provide retrieval-augmented answers."""

    def __init__(
        self,
        agent: BaseAgent,
        store: InMemoryVectorStore,
        context_top_k: int = 3,
    ) -> None:
        self.agent = agent
        self.store = store
        self.context_top_k = context_top_k

    def build_context(self, question: str) -> str:
        results = self.store.search(question, top_k=self.context_top_k)
        if not results:
            return ""
        formatted: List[str] = []
        for doc_id, score, text in results:
            formatted.append(f"[{doc_id} | score={score:.2f}]\n{text.strip()}")
        return "\n\n".join(formatted)

    def ask(self, question: str) -> str:
        context = self.build_context(question)
        if context:
            prompt = (
                "You are answering questions using the provided context. "
                "Cite the source ids in your response when relevant.\n\n"
                f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
            )
        else:
            prompt = (
                "No context was found. Answer using your general knowledge. "
                f"Question: {question}"
            )
        return self.agent.complete(prompt)


def main() -> None:
    print("Loading tutorial RAG agent...")
    memory = ConversationBufferMemory(max_messages=6)
    agent = BaseAgent(
        system_prompt=(
            "You ground answers in provided context. "
            "If the context is missing, acknowledge the gap."
        ),
        memory=memory,
        temperature=0.1,
    )
    store = InMemoryVectorStore()

    docs_dir = Path(__file__).parent / "notes"
    if docs_dir.exists():
        store.add_directory(docs_dir, pattern="*.md")

    store.add_document(
        "rag-basics",
        "Retrieval-augmented generation (RAG) augments prompts with documents "
        "fetched from an external knowledge source before calling the model.",
    )
    store.add_document(
        "planning-overview",
        "Planning agents separate thinking from acting. ReAct interleaves a "
        "chain of thoughts with tool calls.",
    )

    rag_agent = RAGAgent(agent=agent, store=store)
    print(f"Indexed documents: {store.list_ids()}")

    while True:
        question = input("\nAsk a question (or type 'quit'): ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        if not question:
            continue
        answer = rag_agent.ask(question)
        print(f"\nAnswer:\n{answer}")


if __name__ == "__main__":
    main()
