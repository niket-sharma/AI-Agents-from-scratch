"""
Tutorial 14-03: Cross-Session Memory — Mem0 Drop-In

Same cross-session recall demo as 02_hand_rolled_long_term.py, but using
Mem0 (https://mem0.ai) as the memory layer.

Mem0 handles extraction, embedding, storage, and retrieval automatically.
The memory code shrinks from ~50 lines to ~10.

Install: pip install mem0ai
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

try:
    from mem0 import Memory
except ImportError:
    raise SystemExit("mem0ai is not installed. Run: pip install mem0ai")

load_dotenv()

USER_ID = "tutorial_14_user"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def run_session(label: str, inputs: list) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print("=" * 60)

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Mem0 default config: local ChromaDB + OpenAI embeddings
    memory = Memory()

    for user_input in inputs:
        # 1. Retrieve relevant memories for this query
        search_result = memory.search(user_input, user_id=USER_ID, limit=5)
        memories = search_result.get("results", [])

        # 2. Build system prompt from retrieved memories
        system = "You are a helpful personal assistant with long-term memory."
        if memories:
            mem_text = "\n".join(f"- {m['memory']}" for m in memories)
            system += f"\n\nWhat you remember about this user:\n{mem_text}"

        print(f"\nUser : {user_input}")
        if memories:
            print(f"       [Retrieved {len(memories)} memory/memories]")

        # 3. Generate response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_input},
            ],
            max_tokens=250,
        )
        reply = response.choices[0].message.content or ""
        print(f"Agent: {reply}")

        # 4. Store this exchange — Mem0 extracts facts automatically
        memory.add(
            [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": reply},
            ],
            user_id=USER_ID,
        )


# ---------------------------------------------------------------------------
# Demo
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

    print("\n\n[Simulating restart — Mem0 persists automatically via local vector store]\n")

    run_session(
        "SESSION 2 — Fresh process, Mem0 remembers",
        [
            "What do you remember about me?",
            "Which framework did I say I prefer?",
            "What city do I work in?",
        ],
    )

    print(
        "\n\nCompare with 02_hand_rolled_long_term.py — same capability, "
        "Mem0 handles all the plumbing."
    )
