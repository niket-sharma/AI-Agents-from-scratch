from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ToolResult:
    """Standardized response from a tool execution."""

    content: str
    data: Optional[Dict[str, Any]] = None


class BaseTool(ABC):
    """Interface for agent-accessible tools."""

    name: str
    description: str

    def as_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "description": self.description}

    @abstractmethod
    def run(self, input_text: str) -> ToolResult:
        """Execute the tool and return the result."""
