"""
Basic Agent with Microsoft Agent Framework
============================================

Demonstrates the foundational patterns: creating an agent backed by OpenAI,
running a single-turn completion, streaming tokens in real time, and
maintaining a multi-turn conversation using explicit ChatMessage history.

Concepts covered:
    - OpenAIChatClient and .as_agent() for agent creation
    - agent.run()        -> single-turn, returns result with .text
    - agent.run_stream() -> token-by-token streaming
    - List[ChatMessage]  -> manual multi-turn history

Usage:
    python 01_basic_agent.py

Requirements:
    - OPENAI_API_KEY environment variable set
    - pip install -r requirements.txt
"""

import asyncio
import os
from typing import List

from dotenv import load_dotenv

from agent_framework import ChatMessage, Role
from agent_framework.openai import OpenAIChatClient

# ============================================================================
# Environment
# ============================================================================

load_dotenv()

DEFAULT_MODEL = "gpt-4o-mini"


# ============================================================================
# Helpers
# ============================================================================


def _validate_api_key() -> None:
    """Exit with a helpful message when OPENAI_API_KEY is missing.

    Raises:
        SystemExit: If the key is not set in the environment.
    """
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set.")
        print("  1. Create a .env file with  OPENAI_API_KEY=sk-...")
        print("  2. Or export it in your shell.")
        raise SystemExit(1)


def _create_agent(name: str = "BasicAgent", instructions: str = "You are a helpful assistant."):
    """Factory: instantiate an agent with the given name and instructions.

    Args:
        name:         Display name shown in log / print statements.
        instructions: System-prompt text the LLM receives.

    Returns:
        A ChatAgent ready for .run() or .run_stream().
    """
    return OpenAIChatClient(model_id=DEFAULT_MODEL).as_agent(
        name=name,
        instructions=instructions,
    )


# ============================================================================
# Demo 1 — single-turn run
# ============================================================================


async def demo_basic_run() -> None:
    """Single-turn: one message in, one message out.  No history kept."""
    _validate_api_key()

    print("\n" + "=" * 80)
    print("  DEMO 1: Basic Single-Turn Run")
    print("=" * 80)

    agent = _create_agent(
        name="GreetingAgent",
        instructions="You are a friendly assistant. Keep replies under 3 sentences.",
    )

    prompt = "Hello! Can you introduce yourself?"
    print(f"\n[User]           {prompt}")

    result = await agent.run(prompt)
    print(f"[GreetingAgent]  {result.text}\n")


# ============================================================================
# Demo 2 — streaming
# ============================================================================


async def demo_streaming() -> None:
    """Stream tokens as they arrive, giving a live-typing feel.

    agent.run_stream() yields chunk objects; each chunk with a non-empty
    .text field is one or more tokens.  Printing with end="" produces the
    streaming appearance.
    """
    _validate_api_key()

    print("\n" + "=" * 80)
    print("  DEMO 2: Streaming Response")
    print("=" * 80)

    agent = _create_agent(
        name="StreamAgent",
        instructions="You are a storyteller. Tell a short 3-sentence story.",
    )

    prompt = "Tell me a story about a robot exploring the ocean."
    print(f"\n[User]         {prompt}")
    print("[StreamAgent] ", end="", flush=True)

    async for chunk in agent.run_stream(prompt):
        if chunk.text:
            print(chunk.text, end="", flush=True)

    print("\n")  # newline after stream ends


# ============================================================================
# Demo 3 — multi-turn interactive chat
# ============================================================================


async def demo_multi_turn() -> None:
    """Interactive loop that keeps a full ChatMessage history.

    Each user message is appended as Role.USER; each reply is appended as
    Role.ASSISTANT.  The full list is passed to agent.run() on every turn so
    the model has complete context.

    Type 'quit', 'exit', or 'bye' to end the session.
    """
    _validate_api_key()

    print("\n" + "=" * 80)
    print("  DEMO 3: Multi-Turn Interactive Chat")
    print("=" * 80)
    print("\nThe agent remembers everything you say in this session.")
    print("Type 'quit', 'exit', or 'bye' to end.\n")

    agent = _create_agent(
        name="ChatBot",
        instructions=(
            "You are a knowledgeable but concise assistant. "
            "Remember the context of this conversation and refer back to "
            "earlier messages when relevant. Keep replies to 2-4 sentences."
        ),
    )

    # Accumulates the full conversation for context continuity
    history: List[ChatMessage] = []

    while True:
        try:
            user_input = input("[You] ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.lower() in ("quit", "exit", "bye", "q"):
            print("\n[ChatBot] Goodbye!\n")
            break

        if not user_input:
            continue

        # Append user turn
        history.append(ChatMessage(Role.USER, text=user_input))

        # Pass the full history so the model has context from prior turns
        result = await agent.run(history)

        reply: str = result.text
        print(f"[ChatBot] {reply}\n")

        # Append assistant turn for next iteration
        history.append(ChatMessage(Role.ASSISTANT, text=reply))


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    # Primary demo: multi-turn interactive chat (the most complete experience).
    # Uncomment one of the lines below to run a specific demo instead.

    asyncio.run(demo_multi_turn())

    # asyncio.run(demo_basic_run())
    # asyncio.run(demo_streaming())
