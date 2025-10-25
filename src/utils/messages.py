from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Literal, Optional


class Role(str, Enum):
    """Conversation roles understood by chat completion APIs."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """Simple representation of a chat message."""

    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        data: Dict[str, str] = {"role": self.role, "content": self.content}
        if self.name:
            data["name"] = self.name
        if self.tool_call_id:
            data["tool_call_id"] = self.tool_call_id
        return data
