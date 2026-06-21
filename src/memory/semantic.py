from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Optional


class SemanticMemory:
    """
    Extracts and persists durable facts from conversations via an LLM call,
    then retrieves relevant facts by keyword overlap.

    Unlike episodic memory (which stores raw turns), semantic memory stores
    *distilled* knowledge — things that stay true across sessions:
    "user prefers Python", "user works at a fintech startup".

    Not a BaseMemory subclass — it supplements an agent's system context
    rather than replacing the conversation buffer.
    """

    def __init__(
        self,
        client: Any,
        storage_path: str = "./semantic_memory.json",
        model: str = "gpt-4o-mini",
    ) -> None:
        self._client = client
        self._storage_path = Path(storage_path)
        self._model = model
        self._facts: List[str] = self._load()

    # ------------------------------------------------------------------ #
    # Persistence                                                          #
    # ------------------------------------------------------------------ #

    def _load(self) -> List[str]:
        if self._storage_path.exists():
            return json.loads(self._storage_path.read_text())
        return []

    def _save(self) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(json.dumps(self._facts, indent=2))

    # ------------------------------------------------------------------ #
    # Core API                                                             #
    # ------------------------------------------------------------------ #

    def extract_and_store(self, text: str) -> List[str]:
        """
        Ask the LLM to extract concrete, durable facts from *text*, add any
        new ones to storage, and return the newly found facts.
        """
        prompt = (
            "Extract concise, durable facts from the text below. "
            "Return one fact per line. Only include specific, concrete facts "
            "(names, roles, preferences, constraints, locations). "
            "Skip generic or conversational statements.\n\n"
            f"Text: {text}\n\nFacts (one per line):"
        )
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        raw = response.choices[0].message.content or ""
        new_facts = [
            line.lstrip("-•* ").strip()
            for line in raw.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        added: List[str] = []
        for fact in new_facts:
            if fact and fact not in self._facts:
                self._facts.append(fact)
                added.append(fact)
        if added:
            self._save()
        return added

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """Return facts most relevant to *query* by word-overlap scoring."""
        if not self._facts:
            return []
        query_words = set(query.lower().split())
        scored = sorted(
            self._facts,
            key=lambda f: len(query_words & set(f.lower().split())),
            reverse=True,
        )
        top = [f for f in scored[:top_k] if any(w in f.lower() for w in query_words)]
        return top if top else self._facts[:top_k]

    def as_context(self, query: str) -> str:
        """Format relevant facts as a block suitable for a system prompt."""
        facts = self.retrieve(query)
        if not facts:
            return ""
        return "Relevant facts about the user:\n" + "\n".join(f"- {f}" for f in facts)

    @property
    def all_facts(self) -> List[str]:
        return list(self._facts)

    def clear(self) -> None:
        self._facts.clear()
        self._save()
