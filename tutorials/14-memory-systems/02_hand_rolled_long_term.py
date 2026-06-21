"""
Tutorial 14-02: Cross-Session Memory — Hand-Rolled

Demonstrates an agent that remembers you across process restarts using
the src/memory classes built in this phase:

  EpisodicMemory  — stores conversation turns in ChromaDB (vector similarity)
  SemanticMemory  — extracts durable facts via LLM, persists to JSON
  SummaryMemory   — keeps context within a token budget via rolling summarization

Run this script twice to see cross-session recall in action.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from src.agent.base import BaseAgent
from src.memory.episodic import EpisodicMemory
from src.memory.semantic import SemanticMemory
from src.memory.summary import SummaryMemory

load_dotenv()

# All session data lands here — delete this directory to start fresh
PERSIST_DIR = "./demo_memory"
SEMANTIC_PATH = f"{PERSIST_DIR}/facts.json"
COLLECTION = "tutorial_14_episodes"

Path(PERSIST_DIR).mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Helper: run one conversation session
# ---------------------------------------------------------------------------

def run_session(label: str, inputs: list) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print("=" * 60)

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Episodic memory — persists to ChromaDB at PERSIST_DIR
    episodic = EpisodicMemory(
        collection_name=COLLECTION,
        persist_dir=PERSIST_DIR,
        top_k=6,
    )

    # Semantic memory — extracts facts and persists to JSON
    semantic = SemanticMemory(client=client, storage_path=SEMANTIC_PATH)

    # Build the system prompt with any previously known facts
    known_facts = semantic.as_context("user profile")
    system = (
        "You are a helpful personal assistant with long-term memory. "
        "Use the conversation context to personalize every response."
    )
    if known_facts:
        system += f"\n\n{known_facts}"

    agent = BaseAgent(
        system_prompt=system,
        memory=episodic,
        client=client,
        model="gpt-4o-mini",
    )

    for user_input in inputs:
        print(f"\nUser : {user_input}")
        response = agent.run_step(user_input)
        print(f"Agent: {response}")

        # Extract durable facts from what the user just said
        new_facts = semantic.extract_and_store(f"User said: {user_input}")
        if new_facts:
            print(f"       [Extracted {len(new_facts)} fact(s): {new_facts}]")

    total_facts = len(semantic.all_facts)
    total_episodes = episodic._collection.count()
    print(f"\n  Memory store: {total_episodes} episodes, {total_facts} facts")


# ---------------------------------------------------------------------------
# Demo: two simulated sessions
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_session(
        "SESSION 1 — Introducing yourself",
        [
            "Hi! My name is Alice. I'm a backend engineer who loves Python.",
            "My favourite framework is FastAPI and I work at a fintech startup in London.",
            "I'm currently learning about AI agents and long-term memory.",
        ],
    )

    print("\n\n[Simulating process restart — creating fresh Python objects, same persist_dir]\n")

    run_session(
        "SESSION 2 — Fresh process, persistent memory",
        [
            "What do you remember about me?",
            "Which framework did I say I prefer?",
            "What city do I work in?",
        ],
    )

    print(
        "\n\nTip: delete the './demo_memory' directory to wipe all stored memories and start fresh."
    )
