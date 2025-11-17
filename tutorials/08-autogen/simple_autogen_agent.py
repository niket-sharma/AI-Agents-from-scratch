"""
Tutorial 08: Build an agent with AutoGen.

This script wires together AutoGen/AG2 primitives (`LLMConfig`, `AssistantAgent`,
`UserProxyAgent`, and `RunResponse`) so you can see how a "from-scratch" agent
is built before we move back into the repo's `src/` framework.
"""

from __future__ import annotations

import os
from typing import Any, Iterable, Tuple

from dotenv import load_dotenv
from autogen import AssistantAgent, LLMConfig, UserProxyAgent

DEFAULT_MODEL = "gpt-4o-mini"
USER_PROMPT = (
    "I want to learn how to build an AutoGen-based agent step by step. "
    "Summarize what AutoGen does and outline at least three steps I should take to practice."
)


def build_llm_config(model: str | None = None, temperature: float = 0.3) -> LLMConfig:
    """Create an LLMConfig that AutoGen understands."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required to run this tutorial.")

    return LLMConfig(
        {
            "model": model or DEFAULT_MODEL,
            "api_key": api_key,
            "temperature": temperature,
        }
    )


def configure_agents(llm_config: LLMConfig) -> Tuple[AssistantAgent, UserProxyAgent]:
    """Create a helper assistant and a proxy user to drive the conversation."""
    assistant_prompt = (
        "You are a concise researcher assistant. When a question arrives, "
        "summarize the request, outline a plan with bullet points, then answer it."
    )

    assistant = AssistantAgent(
        name="autogen_assistant",
        system_message=assistant_prompt,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    human_proxy = UserProxyAgent(
        name="autogen_user",
        description="Human proxy that injects requests and reviews the assistant's plan.",
        human_input_mode="NEVER",
    )

    return assistant, human_proxy


def format_messages(messages: Iterable[dict[str, Any]]) -> Iterable[str]:
    """Convert AutoGen message records into readable strings."""
    for message in messages:
        content = message.get("content")
        if isinstance(content, list):
            content = "\n".join(str(part) for part in content)
        yield f'{message.get("name") or message.get("role")}: {content}'


def main() -> None:
    load_dotenv(override=True)
    llm_config = build_llm_config()
    assistant, human_proxy = configure_agents(llm_config)

    run_response = human_proxy.run(
        assistant,
        message=USER_PROMPT,
        max_turns=4,
        clear_history=True,
        summary_method="last_msg",
    )

    run_response.process()

    print("\n=== Conversation ===")
    for line in format_messages(run_response.messages):
        print(line)

    print("\n=== Summary ===")
    print(run_response.summary)


if __name__ == "__main__":
    main()
