"""
Multi-agent collaboration example with manager, workers, and reviewer roles.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import BaseAgent
from src.memory import ConversationBufferMemory
from src.planning import ReActPlanner, TaskDecomposer, ThoughtStep
from src.tools import CalculatorTool


def _default_memory() -> ConversationBufferMemory:
    return ConversationBufferMemory(max_messages=8)


@dataclass
class TaskResult:
    subtask: str
    answer: str
    steps: List[ThoughtStep]


class AgentTeam:
    """
    Coordinates specialized agents to deliver higher-quality responses.
    """

    def __init__(self) -> None:
        self.manager = BaseAgent(
            system_prompt=(
                "You are a project manager. Break complex objectives into "
                "clear, ordered subtasks."
            ),
            memory=_default_memory(),
            temperature=0.2,
        )
        self.research_agent = BaseAgent(
            system_prompt=(
                "You are a research specialist. Gather concise facts, cite sources, "
                "and highlight uncertainties."
            ),
            memory=_default_memory(),
            temperature=0.3,
        )
        self.analysis_agent = BaseAgent(
            system_prompt=(
                "You are an analytical expert. Interpret data, perform comparisons, "
                "and compute estimates. Use the calculator tool for math."
            ),
            memory=_default_memory(),
            temperature=0.2,
        )
        self.reviewer_agent = BaseAgent(
            system_prompt=(
                "You are a meticulous reviewer. Identify missing requirements, "
                "factual gaps, or unclear explanations. Suggest improvements."
            ),
            memory=_default_memory(),
            temperature=0.1,
        )
        self.calculator = CalculatorTool()
        self.planner = ReActPlanner(tools=[self.calculator], max_steps=5)
        self.decomposer = TaskDecomposer(max_steps=6)

    def _assign_agent(self, subtask: str) -> BaseAgent:
        lowered = subtask.lower()
        if any(keyword in lowered for keyword in ["calculate", "estimate", "compare", "analyze", "cost"]):
            return self.analysis_agent
        return self.research_agent

    def _execute_subtask(self, agent: BaseAgent, subtask: str) -> TaskResult:
        answer, steps = self.planner.run(question=subtask, agent=agent)
        if not answer and steps and steps[-1].observation:
            answer = steps[-1].observation
        return TaskResult(subtask=subtask, answer=answer, steps=steps)

    def _format_results(self, results: List[TaskResult]) -> str:
        lines: List[str] = []
        for result in results:
            lines.append(f"Subtask: {result.subtask}")
            lines.append(f"Answer: {result.answer or 'No answer produced'}")
            lines.append("Steps:")
            for step in result.steps:
                if step.thought:
                    lines.append(f"- Thought: {step.thought}")
                if step.action:
                    lines.append(f"  Action: {step.action} | Input: {step.action_input}")
                if step.observation:
                    lines.append(f"  Observation: {step.observation}")
            lines.append("")
        return "\n".join(lines)

    def handle_request(self, goal: str, max_revisions: int = 1) -> Dict[str, str]:
        subtasks = self.decomposer.decompose(goal=goal, agent=self.manager)
        if not subtasks:
            subtasks = [goal]
        results: List[TaskResult] = []
        for subtask in subtasks:
            agent = self._assign_agent(subtask)
            results.append(self._execute_subtask(agent, subtask))

        draft = self._format_results(results)
        review_prompt = (
            "Review the following multi-agent draft. Identify any issues, "
            "missing information, or places where the reasoning should be "
            "expanded. Provide feedback as bullet points. If everything looks "
            "solid, say 'Looks good.'\n\n"
            f"Draft:\n{draft}"
        )
        feedback = self.reviewer_agent.complete(review_prompt)

        revision_summary = draft
        revisions_left = max_revisions
        while revisions_left > 0 and "Looks good" not in feedback:
            revisions_left -= 1
            improvement_prompt = (
                "Improve the report based on this feedback. Keep the structure "
                "clear and actionable.\n\n"
                f"Original Draft:\n{draft}\n\nFeedback:\n{feedback}"
            )
            revision_summary = self.manager.complete(improvement_prompt)
            if revisions_left:
                follow_up_prompt = (
                    "Does the revised report address the feedback? "
                    "Respond with 'Looks good' or list remaining issues.\n\n"
                    f"Revised Draft:\n{revision_summary}\n\nFeedback:\n{feedback}"
                )
                feedback = self.reviewer_agent.complete(follow_up_prompt)
            else:
                break

        return {
            "goal": goal,
            "subtasks": "\n".join(f"- {item}" for item in subtasks),
            "draft": draft,
            "feedback": feedback,
            "final_report": revision_summary,
        }


def main() -> None:
    team = AgentTeam()
    goal = input("Describe the project for the agent team:\n> ").strip()
    if not goal:
        print("No goal provided. Exiting.")
        return
    result = team.handle_request(goal)
    print("\n--- Subtasks ---")
    print(result["subtasks"])
    print("\n--- Reviewer Feedback ---")
    print(result["feedback"])
    print("\n--- Final Report ---")
    print(result["final_report"])


if __name__ == "__main__":
    main()
