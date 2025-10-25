"""
Example: research assistant that performs structured investigations.
"""

from __future__ import annotations

from typing import List
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import BaseAgent
from src.planning import ReActPlanner, TaskDecomposer
from src.tools import CalculatorTool


def run_research(query: str) -> str:
    planner_prompt = (
        "You are a methodical research analyst. Use the calculator for numeric "
        "estimates. Provide cited, concise findings."
    )
    agent = BaseAgent(system_prompt=planner_prompt, temperature=0.2)
    planner = ReActPlanner(tools=[CalculatorTool()], max_steps=5)
    decomposer = TaskDecomposer(max_steps=4)

    subtasks = decomposer.decompose(goal=query, agent=agent)
    if not subtasks:
        subtasks = [query]
    answers: List[str] = []
    for subtask in subtasks:
        answer, _ = planner.run(question=subtask, agent=agent)
        answers.append(f"- {subtask}: {answer}")
    synthesis_prompt = (
        "Synthesize the following research notes into a polished answer. "
        "Provide citations when possible.\n\n"
        f"Notes:\n{chr(10).join(answers)}"
    )
    return agent.complete(synthesis_prompt)


def main() -> None:
    query = input("What topic should the research agent investigate?\n> ").strip()
    if not query:
        print("No query provided. Exiting.")
        return
    answer = run_research(query)
    print("\n--- Research Summary ---")
    print(answer)


if __name__ == "__main__":
    main()
