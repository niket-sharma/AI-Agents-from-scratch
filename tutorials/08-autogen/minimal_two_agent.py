"""
Minimal 2-agent AutoGen chat.

UserProxyAgent asks: "Explain PCA in 3 bullet points".
AssistantAgent replies. The script prints the full message history.
"""

from __future__ import annotations

import os
from typing import Any, Iterable

from dotenv import load_dotenv
from autogen import AssistantAgent, LLMConfig, UserProxyAgent

DEFAULT_MODEL = "gpt-4o-mini"
USER_PROMPT = "Explain PCA in 3 bullet points."


def build_llm_config() -> LLMConfig:
    """Configure the model and API key for AutoGen."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required.")

    return LLMConfig(
        {
            "model": DEFAULT_MODEL,
            "api_key": api_key,
            "temperature": 0.3,
        }
    )


def format_messages(messages: Iterable[dict[str, Any]]) -> Iterable[str]:
    """Convert AutoGen messages into readable lines."""
    for message in messages:
        content = message.get("content")
        if isinstance(content, list):
            content = "\n".join(str(part) for part in content)
        speaker = message.get("name") or message.get("role")
        yield f"{speaker}: {content}"


def main() -> None:
    load_dotenv(override=True)
    llm_config = build_llm_config()

    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a concise tutor. Answer briefly and clearly.",
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    user = UserProxyAgent(
        name="user",
        human_input_mode="NEVER",
        description="Initiates the request and prints the conversation.",
        code_execution_config={"use_docker": False},
    )

    run_response = user.run(
        assistant,
        message=USER_PROMPT,
        # One assistant reply is enough for this demo.
        max_turns=1,
        clear_history=True,
        summary_method="last_msg",
    )

    # Drain events (ensures the conversation completes).
    run_response.process()

    print("\n=== Conversation ===")
    for line in format_messages(run_response.messages):
        print(line)


if __name__ == "__main__":
    main()
