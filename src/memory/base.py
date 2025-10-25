from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List

from src.utils import Message


class BaseMemory(ABC):
    """Abstract base for conversation memory implementations."""

    def __init__(self) -> None:
        self._messages: List[Message] = []

    def add(self, message: Message) -> None:
        self._messages.append(message)

    def extend(self, messages: Iterable[Message]) -> None:
        self._messages.extend(messages)

    @abstractmethod
    def get_context(self) -> List[Message]:
        """Return messages to send to the model."""

    def reset(self) -> None:
        self._messages.clear()

    @property
    def messages(self) -> List[Message]:
        return list(self._messages)
