"""
Tutorial 14-04: Letta Runtime (Optional — heavier setup required)

Letta (formerly MemGPT) models memory as a first-class part of the agent's
*job*, not just a retrieval layer bolted on the side. The agent itself decides
what to remember, what to forget, and what to surface.

Letta's memory model has three tiers:
  Core memory   — always in-context; limited size; the agent curates this.
  Recall memory — searchable episodic store (like our EpisodicMemory).
  Archival memory — unlimited write-once store for long-term facts.

Setup (one-time):
  pip install letta
  letta server          # starts local Letta server on :8283
  letta create user     # creates a default user

Then run this script.

Docs: https://docs.letta.com
"""

try:
    from letta import create_client
    from letta.schemas.memory import ChatMemory
    from letta.schemas.llm_config import LLMConfig
    from letta.schemas.embedding_config import EmbeddingConfig
except ImportError:
    raise SystemExit(
        "Letta is not installed.\n"
        "Install: pip install letta\n"
        "Start server: letta server\n"
        "Then re-run this script."
    )


def main() -> None:
    # Connect to local Letta server
    client = create_client()

    # Each Letta agent gets a persistent identity and tiered memory
    agent = client.create_agent(
        name="letta_tutorial_agent",
        llm_config=LLMConfig.default(),
        embedding_config=EmbeddingConfig.default(),
        memory=ChatMemory(
            # Core memory blocks — always in-context, agent can edit these
            human="Name: unknown\nRole: unknown",
            persona="I am a helpful assistant with excellent long-term memory.",
        ),
    )
    print(f"Created agent: {agent.id}")

    # --- Session 1 --------------------------------------------------------
    print("\n--- Session 1: Introducing yourself ---")
    messages = [
        "Hi! My name is Alice. I'm a backend engineer who loves Python.",
        "My favourite framework is FastAPI and I work at a fintech startup.",
    ]
    for msg in messages:
        print(f"User : {msg}")
        response = client.send_message(agent_id=agent.id, role="user", message=msg)
        for m in response.messages:
            if hasattr(m, "assistant_message") and m.assistant_message:
                print(f"Agent: {m.assistant_message}")

    # --- Session 2 (same agent_id = persistent memory) --------------------
    print("\n--- Session 2 (same agent_id, memory persisted) ---")
    recall_queries = [
        "What do you remember about me?",
        "What's my favourite framework?",
    ]
    for msg in recall_queries:
        print(f"User : {msg}")
        response = client.send_message(agent_id=agent.id, role="user", message=msg)
        for m in response.messages:
            if hasattr(m, "assistant_message") and m.assistant_message:
                print(f"Agent: {m.assistant_message}")

    # Show what's in core memory (the agent's editable notepad)
    agent_state = client.get_agent(agent.id)
    print("\n--- Core memory (agent's notepad) ---")
    for block in agent_state.memory.to_dict()["memory"].values():
        print(f"  {block}")


if __name__ == "__main__":
    main()
