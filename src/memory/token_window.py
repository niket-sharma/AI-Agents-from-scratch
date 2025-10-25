from __future__ import annotations

from typing import List

from src.memory.base import BaseMemory
from src.utils import Message

try:
    import tiktoken
except ImportError:  # pragma: no cover
    tiktoken = None  # type: ignore


def _estimate_tokens(text: str) -> int:
    """Fallback token estimator if tiktoken is unavailable."""
    return max(1, len(text.split()))


class TokenWindowMemory(BaseMemory):
    """
    Maintains conversation history constrained by a token budget.

    This is a simplified token-aware buffer suitable for teaching.
    """

    def __init__(self, model: str = "gpt-3.5-turbo", max_tokens: int = 2000) -> None:
        super().__init__()
        self.model = model
        self.max_tokens = max_tokens
        if tiktoken:
            self._encoder = tiktoken.encoding_for_model(model)
        else:  # pragma: no cover
            self._encoder = None

    def _count(self, text: str) -> int:
        if self._encoder:
            return len(self._encoder.encode(text))
        return _estimate_tokens(text)

    def get_context(self) -> List[Message]:
        messages: List[Message] = []
        total_tokens = 0
        for message in reversed(self.messages):
            message_tokens = self._count(message.content)
            if total_tokens + message_tokens > self.max_tokens:
                break
            messages.append(message)
            total_tokens += message_tokens
        messages.reverse()
        return messages
