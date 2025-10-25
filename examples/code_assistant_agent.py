"""
Example: code assistant agent that reviews snippets and suggests improvements.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import ChatAgent
from src.memory import TokenWindowMemory


SYSTEM_PROMPT = (
    "You are an experienced software engineer. Provide code improvements, "
    "spot bugs, and explain reasoning concisely. When appropriate, suggest "
    "tests the user can write."
)


def main() -> None:
    ChatAgent(
        system_prompt=SYSTEM_PROMPT,
        memory=TokenWindowMemory(model="gpt-4o-mini", max_tokens=1500),
        temperature=0.2,
    ).chat(
        welcome=(
            "Code Assistant Agent\n"
            "Paste code snippets or describe issues for targeted feedback."
        )
    )


if __name__ == "__main__":
    main()
