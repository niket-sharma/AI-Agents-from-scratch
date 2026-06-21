from __future__ import annotations

from typing import Any, List, Optional

from src.memory.base import BaseMemory
from src.utils.messages import Message

try:
    import tiktoken
except ImportError:  # pragma: no cover
    tiktoken = None  # type: ignore


class SummaryMemory(BaseMemory):
    """
    Rolling summarization memory — keeps conversation history within a token
    budget by compacting old messages into a running summary via an LLM call.

    When total tokens exceed *max_tokens*, the oldest half of the buffer is
    summarized and replaced with a single [Conversation summary: ...] message.
    The summary accumulates across multiple compaction cycles so no context
    is permanently lost.
    """

    def __init__(
        self,
        client: Any,
        model: str = "gpt-4o-mini",
        max_tokens: int = 2000,
        summary_model: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._client = client
        self._model = model
        self._max_tokens = max_tokens
        self._summary_model = summary_model or model
        self._summary: Optional[str] = None

        if tiktoken:
            try:
                self._encoder = tiktoken.encoding_for_model(model)
            except KeyError:
                self._encoder = tiktoken.get_encoding("cl100k_base")
        else:  # pragma: no cover
            self._encoder = None

    # ------------------------------------------------------------------ #
    # Token counting                                                       #
    # ------------------------------------------------------------------ #

    def _count(self, text: str) -> int:
        if self._encoder:
            return len(self._encoder.encode(text))
        return max(1, len(text.split()))

    def _total_tokens(self) -> int:
        total = sum(self._count(m.content) for m in self._messages)
        if self._summary:
            total += self._count(self._summary)
        return total

    @property
    def token_count(self) -> int:
        return self._total_tokens()

    # ------------------------------------------------------------------ #
    # Compaction                                                           #
    # ------------------------------------------------------------------ #

    def _compact(self) -> None:
        if len(self._messages) < 2:
            return

        # Keep the more-recent half; summarize everything older
        keep_n = max(2, len(self._messages) // 2)
        to_summarize = self._messages[:-keep_n]
        self._messages = self._messages[-keep_n:]

        history = "\n".join(f"{m.role}: {m.content}" for m in to_summarize)
        if self._summary:
            history = f"[Prior summary]: {self._summary}\n\n{history}"

        prompt = (
            "Summarize the following conversation concisely. "
            "Preserve all key facts, names, decisions, preferences, and context "
            "that a future assistant would need:\n\n" + history
        )
        response = self._client.chat.completions.create(
            model=self._summary_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        self._summary = (response.choices[0].message.content or "").strip()

    # ------------------------------------------------------------------ #
    # BaseMemory interface                                                 #
    # ------------------------------------------------------------------ #

    def add(self, message: Message) -> None:
        super().add(message)
        if self._total_tokens() > self._max_tokens:
            self._compact()

    def get_context(self) -> List[Message]:
        messages: List[Message] = []
        if self._summary:
            messages.append(
                Message(role="system", content=f"[Conversation summary: {self._summary}]")
            )
        messages.extend(self._messages)
        return messages

    def reset(self) -> None:
        super().reset()
        self._summary = None

    @property
    def summary(self) -> Optional[str]:
        return self._summary
