from __future__ import annotations

from typing import Deque, List
from collections import deque

from src.memory.base import BaseMemory
from src.utils import Message


class ConversationBufferMemory(BaseMemory):
    """Keeps a fixed number of most recent messages."""

    def __init__(self, max_messages: int = 10) -> None:
        super().__init__()
        self.max_messages = max_messages
        self._buffer: Deque[Message] = deque(maxlen=max_messages)

    def add(self, message: Message) -> None:
        self._buffer.append(message)
        super().add(message)

    def extend(self, messages: List[Message]) -> None:
        for message in messages:
            self.add(message)

    def get_context(self) -> List[Message]:
        return list(self._buffer)

    def reset(self) -> None:
        self._buffer.clear()
        super().reset()
