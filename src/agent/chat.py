from __future__ import annotations

from typing import Optional

from src.agent.base import BaseAgent


class ChatAgent(BaseAgent):
    """Interactive command-line chat agent."""

    def chat(self, welcome: Optional[str] = None) -> None:
        if welcome:
            print(welcome)
        print("Type 'quit' or 'exit' to stop.\n")
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            if user_input.lower() in {"quit", "exit"}:
                print("Goodbye!")
                break
            if not user_input:
                continue
            response = self.run_step(user_input)
            print(f"Agent: {response}\n")
