from __future__ import annotations

from typing import Callable, List, Optional

from src.agent.base import BaseAgent


class TaskDecomposer:
    """
    Utility to break a complex objective into smaller steps.

    Works with a provided heuristic function or an LLM-backed agent.
    """

    def __init__(self, max_steps: int = 5) -> None:
        self.max_steps = max_steps

    def decompose(
        self,
        goal: str,
        agent: Optional[BaseAgent] = None,
        heuristic: Optional[Callable[[str], List[str]]] = None,
    ) -> List[str]:
        if heuristic:
            steps = heuristic(goal)
            return steps[: self.max_steps]
        if not agent:
            raise ValueError("Provide either an agent or a heuristic callable.")
        prompt = (
            "Break the following objective into a numbered list of actionable steps. "
            "Keep each step concise and focused on a single action. "
            f"Goal: {goal}"
        )
        response = agent.complete(prompt, temperature=0)
        extracted: List[str] = []
        for line in response.splitlines():
            line = line.strip()
            if not line:
                continue
            if line[0].isdigit():
                _, _, content = line.partition(".")
                extracted.append(content.strip() or line)
            else:
                extracted.append(line)
        return extracted[: self.max_steps]
