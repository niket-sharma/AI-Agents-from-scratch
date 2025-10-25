from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from src.agent.base import BaseAgent
from src.tools import BaseTool


@dataclass
class ThoughtStep:
    """Represents a single ReAct iteration."""

    thought: str
    action: Optional[str] = None
    action_input: Optional[str] = None
    observation: Optional[str] = None
    final_answer: Optional[str] = None


Policy = Callable[[str, str, List[ThoughtStep]], str]


class ReActPlanner:
    """
    Minimal ReAct planner implementation for educational use.

    The planner formats the intermediate trajectory and either calls an LLM
    through the provided agent or a custom policy callable (useful for tests).
    """

    def __init__(
        self,
        tools: Iterable[BaseTool],
        max_steps: int = 5,
        instructions: Optional[str] = None,
    ) -> None:
        self.tools: Dict[str, BaseTool] = {tool.name: tool for tool in tools}
        self.max_steps = max_steps
        self.instructions = instructions or (
            "Use the ReAct pattern. Respond with lines formatted as:\n"
            "Thought: your reasoning\n"
            "Action: tool name or Finish\n"
            "Action Input: arguments for the tool (if any)\n"
            "Observation: tool result (if an action was taken)\n"
            "Final Answer: only include when ready to answer the original question."
        )

    def _format_prompt(self, question: str, steps: List[ThoughtStep]) -> str:
        tool_descriptions = "\n".join(
            f"- {tool.name}: {tool.description}" for tool in self.tools.values()
        )
        trajectory_lines: List[str] = []
        for index, step in enumerate(steps, start=1):
            trajectory_lines.append(f"Step {index}:")
            trajectory_lines.append(f"Thought: {step.thought}")
            if step.action:
                trajectory_lines.append(f"Action: {step.action}")
            if step.action_input:
                trajectory_lines.append(f"Action Input: {step.action_input}")
            if step.observation:
                trajectory_lines.append(f"Observation: {step.observation}")
            if step.final_answer:
                trajectory_lines.append(f"Final Answer: {step.final_answer}")
        trajectory = "\n".join(trajectory_lines) if trajectory_lines else "None yet."

        prompt = (
            f"You are assisting with a multi-step reasoning task.\n"
            f"{self.instructions}\n\n"
            f"Available tools:\n{tool_descriptions or '- (no tools available)'}\n\n"
            f"Question: {question}\n"
            f"Trajectory so far:\n{trajectory}\n\n"
            f"Provide the next Thought/Action pair. "
            f"Use 'Action: Finish' when you can give a final answer."
        )
        return prompt

    def _parse_step(self, raw: str) -> ThoughtStep:
        thought, action, action_input, observation, final_answer = (
            None,
            None,
            None,
            None,
            None,
        )
        for line in raw.splitlines():
            if ":" not in line:
                continue
            label, value = line.split(":", 1)
            value = value.strip()
            label_lower = label.lower().strip()
            if label_lower == "thought":
                thought = value
            elif label_lower == "action":
                action = value
            elif label_lower == "action input":
                action_input = value
            elif label_lower == "observation":
                observation = value
            elif label_lower == "final answer":
                final_answer = value
        if not thought:
            thought = raw.strip()
        return ThoughtStep(
            thought=thought,
            action=action,
            action_input=action_input,
            observation=observation,
            final_answer=final_answer,
        )

    def run(
        self,
        question: str,
        agent: BaseAgent,
        policy: Optional[Policy] = None,
    ) -> Tuple[str, List[ThoughtStep]]:
        steps: List[ThoughtStep] = []
        final_answer: str = ""
        for _ in range(self.max_steps):
            prompt = self._format_prompt(question, steps)
            raw = policy(prompt, question, steps) if policy else agent.complete(prompt)
            step = self._parse_step(raw)
            if step.action and step.action.lower() == "finish":
                final_answer = step.final_answer or ""
                steps.append(step)
                break
            if step.action and step.action in self.tools:
                observation = self.tools[step.action].run(step.action_input or "")
                step.observation = observation.content
            steps.append(step)
            if step.final_answer:
                final_answer = step.final_answer
                break
            if step.observation and not step.action:
                final_answer = step.observation
                break
        else:
            if steps and steps[-1].observation:
                final_answer = steps[-1].observation

        return final_answer, steps
