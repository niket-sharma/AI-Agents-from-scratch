# Memory in AI Agents — A Taxonomy

## Why memory matters

Every LLM call is stateless. Without explicit memory, your agent starts from scratch on every turn — it cannot remember a user's name, preferences, or what happened two turns ago. The four memory types below map to how *human* memory is organized, and each solves a different problem in agent design.

---

## The Four Memory Tiers

### 1. Working Memory (in-context / token window)

**What it is:** The messages currently in the prompt — the model's "attention span."

**How it works:** Everything in `messages=[...]` is working memory. When the window fills up, the oldest content falls out (or triggers an error).

**When to use:** Always present; this is the baseline.

```python
# Simple buffer — no token tracking, just keeps the last N messages
memory = ConversationBufferMemory(max_messages=10)
```

**Limit:** Token budget. GPT-4o has ~128k tokens; Gemini 1.5 has ~1M. Doesn't survive restarts.

---

### 2. Episodic Memory (vector store / past events)

**What it is:** A record of past *events* — specific exchanges, task runs, or observations.

**Analogy:** Human episodic memory — "I remember the conversation where Alice told me she prefers dark mode."

**How it works:** Each message is embedded and stored in a vector DB. At retrieval time, the current query is embedded and the most semantically similar past episodes are fetched and injected into the prompt.

```
Session 1:  User says "My name is Alice, I love Python"
            → stored in ChromaDB as embedding

Session 2:  User asks "What do you remember about me?"
            → query is embedded → "My name is Alice, I love Python" retrieved → injected as context
```

**When to use:** Cross-session memory, long-running assistants, personal agents.

**Limit:** Retrieval quality depends on the embedding model. Noisy or off-topic episodes can pollute context. ChromaDB stores up to millions of vectors locally.

---

### 3. Semantic Memory (fact store / distilled knowledge)

**What it is:** Durable, structured facts extracted from conversations — things that are *generally true*, not tied to a specific episode.

**Analogy:** Human semantic memory — "I know Alice is a backend engineer" (independent of *when* I learned it).

**How it works:** After each exchange, an LLM extracts facts (`"user name: Alice"`, `"user language: Python"`) and stores them in a JSON file (or a more sophisticated KV store). Retrieval is by keyword or embedding similarity.

```
Conversation: "I work at a fintech startup building APIs in Go"
Extracted facts:
  - User works at a fintech startup
  - User builds APIs
  - User uses Go
```

**When to use:** User profiling, personalization, long-term assistant behavior.

**Limit:** LLM extraction can miss facts or hallucinate. Facts can go stale (user changes jobs, preferences shift).

---

### 4. Procedural Memory (tools / system prompt / skills)

**What it is:** The agent's *capabilities* — what it knows how to do, not what it has experienced.

**Analogy:** Human procedural memory — "I know how to ride a bike" (implicit skill, not a fact or episode).

**How it works:** Encoded in the system prompt (`"You are a research assistant who cites sources"`) and in the tool registry (functions the model can call).

**When to use:** Always. This is the hardest to change at runtime — it's baked into the agent's configuration.

**Limit:** Can't easily adapt to new skills without re-deploying the system prompt or adding new tools.

---

## Memory Tier Comparison

| Tier | Survives restart? | Scoped to | Cost | Best for |
|------|------------------|-----------|------|----------|
| Working (buffer/token) | No | Current session | Low (no extra calls) | Short conversations |
| Episodic (vector DB) | Yes | Per user/session | Medium (embedding + retrieval) | Cross-session recall, long history |
| Semantic (fact store) | Yes | Per user/entity | Low–Medium (LLM extraction, cheap retrieval) | User preferences, facts |
| Procedural (tools/prompt) | Yes | Agent-wide | Upfront only | Agent capabilities |

---

## When to hand-roll vs use Mem0 / Letta / Zep

**Hand-roll when:**
- You need fine-grained control over what gets stored and retrieved
- You're learning — understanding the plumbing makes you a better user of the frameworks
- Your data is sensitive and can't leave your infrastructure
- The use case is simple enough that a framework would add overhead

**Use Mem0 / Letta / Zep when:**
- You want automatic extraction + multi-tier memory without the plumbing
- You need managed, cloud-hosted memory with team-level access
- Your agent needs tiered memory (working → recall → archival) with automatic promotion

**Rule of thumb:** Start hand-rolled to understand the concepts. Graduate to a framework when the plumbing dominates your codebase.

---

## Persistence across sessions — the key insight

The core of cross-session memory is simple: **write to disk on add, read from disk on get_context**.

```
Session ends  →  messages persisted to ChromaDB (episodic) + JSON (semantic)
                 in-memory Python objects destroyed
Session starts →  new Python objects created, load from disk
                  get_context() returns persisted messages
```

This is what `EpisodicMemory` and `SemanticMemory` in `src/memory/` implement.
