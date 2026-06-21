# Tutorial 14 — Memory Systems

**Topic:** Production-grade agent memory  
**Framework:** Custom (`src/memory/`), Mem0, Letta  
**Prerequisites:** Tutorial 01 (basics), Tutorial 02 (buffer memory)  
**Time:** ~45 minutes

---

## What you'll learn

Agents that only remember the current conversation are demos. Production agents need memory that:
- Survives process restarts
- Scales beyond the context window
- Stores *facts* separately from raw conversation history
- Manages token budgets automatically

This tutorial implements all four memory tiers from scratch, then shows Mem0 as a drop-in replacement.

---

## Files

| File | What it teaches |
|------|----------------|
| `01_memory_taxonomy_EXPLAINED.md` | The four memory tiers and when to use each |
| `02_hand_rolled_long_term.py` | Cross-session agent using `EpisodicMemory` + `SemanticMemory` |
| `03_mem0_integration.py` | Same demo with Mem0 (~10 lines of memory code) |
| `04_letta_runtime.py` | Letta's tiered memory model (optional, heavier setup) |

---

## Quick start

```bash
cd tutorials/14-memory-systems
pip install -r requirements.txt

# Run once to introduce yourself
python 02_hand_rolled_long_term.py

# Run again — the agent remembers you
python 02_hand_rolled_long_term.py

# Wipe memory and start fresh
rm -rf ./demo_memory
```

---

## The `src/memory/` classes added in this tutorial

### `EpisodicMemory`
```python
from src.memory import EpisodicMemory

memory = EpisodicMemory(
    collection_name="my_agent",
    persist_dir="./my_memory",   # survives restarts
    top_k=5,
)
agent = BaseAgent(system_prompt="...", memory=memory)
```

Stores every turn as a ChromaDB embedding. `get_context()` retrieves the `top_k` most semantically similar past turns using the latest user message as the query.

### `SemanticMemory`
```python
from src.memory import SemanticMemory

sem = SemanticMemory(client=openai_client, storage_path="./facts.json")
sem.extract_and_store("User said: I work in Python at a fintech startup")
# → persists: ["User works at a fintech startup", "User uses Python"]

sem.as_context("what language does the user use")
# → "Relevant facts about the user:\n- User uses Python"
```

Extracts durable facts via an LLM call and persists them to JSON. Useful for injecting into the system prompt.

### `SummaryMemory`
```python
from src.memory import SummaryMemory

memory = SummaryMemory(client=openai_client, max_tokens=1000)
agent = BaseAgent(system_prompt="...", memory=memory)
# When the conversation exceeds 1000 tokens, old messages are summarized
# and replaced with a [Conversation summary: ...] system message.
```

Keeps context within a token budget via rolling LLM summarization. No information is permanently lost — the summary accumulates.

---

## Mem0 vs hand-rolled (Tutorial 03)

| | Hand-rolled | Mem0 |
|--|-------------|------|
| Lines of memory code | ~50 | ~10 |
| Control | Full | Framework-managed |
| Custom storage backends | Yes | Via config |
| Multi-user | Manual | Built-in (`user_id`) |
| Cost | API calls for extraction | API calls for extraction |

Both use ChromaDB under the hood locally. Mem0 also offers a managed cloud tier.

---

## Key concepts

- **Episodic memory** = "what happened" (events, turns) — retrieved by similarity
- **Semantic memory** = "what is true" (facts, preferences) — retrieved by keyword/embedding
- **Cross-session persistence** = write on `add()`, read on `get_context()`, disk-backed
- **Token budget management** = `SummaryMemory` compacts old history before the context window fills

---

## Acceptance criteria (spec)

- `02_hand_rolled_long_term.py` recalls a fact stated in a previous process run
- `03_mem0_integration.py` achieves the same with <15 lines of memory code
- `tests/test_episodic_memory.py` and `tests/test_summary_memory.py` pass
