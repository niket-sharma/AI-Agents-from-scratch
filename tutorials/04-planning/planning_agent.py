"""
Example planning agent that combines task decomposition and ReAct.
"""

from __future__ import annotations

from typing import List
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import BaseAgent
from src.memory import TokenWindowMemory
from src.planning import ReActPlanner, TaskDecomposer, ThoughtStep
from src.tools import CalculatorTool


SYSTEM_PROMPT = (
    "You are a careful AI assistant. Reason step by step, call tools when "
    "needed, and provide a concise final answer."
)


def format_steps(steps: List[ThoughtStep]) -> str:
    lines: List[str] = []
    for index, step in enumerate(steps, start=1):
        lines.append(f"Step {index}")
        lines.append(f"  Thought: {step.thought}")
        if step.action:
            lines.append(f"  Action: {step.action}")
        if step.action_input:
            lines.append(f"  Action Input: {step.action_input}")
        if step.observation:
            lines.append(f"  Observation: {step.observation}")
        if step.final_answer:
            lines.append(f"  Final Answer: {step.final_answer}")
    return "\n".join(lines)


def solve_subtask(agent: BaseAgent, planner: ReActPlanner, subtask: str) -> str:
    answer, steps = planner.run(question=subtask, agent=agent)
    print(format_steps(steps))
    if answer:
        print(f"Subtask answer: {answer}\n")
    return answer


def main() -> None:
    user_goal = input("Describe the task you want the agent to solve:\n> ").strip()
    if not user_goal:
        print("No task provided. Exiting.")
        return

    memory = TokenWindowMemory(model="gpt-4o-mini", max_tokens=1500)
    agent = BaseAgent(
        system_prompt=SYSTEM_PROMPT,
        memory=memory,
        temperature=0.2,
    )
    calculator = CalculatorTool()
    planner = ReActPlanner(tools=[calculator], max_steps=6)
    decomposer = TaskDecomposer(max_steps=5)

    print("\n--- Decomposing high-level task ---")
    subtasks = decomposer.decompose(goal=user_goal, agent=agent)
    if not subtasks:
        subtasks = [user_goal]
    for idx, subtask in enumerate(subtasks, start=1):
        print(f"{idx}. {subtask}")

    print("\n--- Solving subtasks with ReAct ---")
    answers: List[str] = []
    for subtask in subtasks:
        answers.append(solve_subtask(agent, planner, subtask))

    print("\n--- Final Report ---")
    for index, (subtask, answer) in enumerate(zip(subtasks, answers), start=1):
        print(f"{index}. {subtask}")
        print(f"   Result: {answer or 'No answer produced'}")


if __name__ == "__main__":
    main()
