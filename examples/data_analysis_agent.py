"""
Example: data analysis agent powered by a ReAct planning loop.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import BaseAgent
from src.memory import TokenWindowMemory
from src.planning import ReActPlanner
from src.tools import CalculatorTool


SYSTEM_PROMPT = (
    "You are a business data analyst. Interpret metrics, perform calculations "
    "with the calculator tool when necessary, and explain the impact clearly."
)


def main() -> None:
    agent = BaseAgent(
        system_prompt=SYSTEM_PROMPT,
        memory=TokenWindowMemory(model="gpt-4o-mini", max_tokens=1200),
        temperature=0.2,
    )
    planner = ReActPlanner(tools=[CalculatorTool()], max_steps=4)
    print("Data Analysis Agent")
    print("Describe your dataset or paste metrics. Type 'quit' to exit.\n")

    while True:
        user_input = input("Question: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break
        if not user_input:
            continue
        answer, steps = planner.run(question=user_input, agent=agent)
        print("\nSteps:")
        for idx, step in enumerate(steps, start=1):
            print(f"  {idx}. Thought: {step.thought}")
            if step.action:
                print(f"     Action: {step.action} ({step.action_input})")
            if step.observation:
                print(f"     Observation: {step.observation}")
        print("\nInsight:")
        print(answer or "No answer produced")
        print("\n---\n")


if __name__ == "__main__":
    main()
