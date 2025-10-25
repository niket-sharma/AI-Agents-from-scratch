# Tutorial 05: Advanced Agent Patterns

This tutorial layers advanced capabilities onto the planning agent from
Tutorial 04. You will add lightweight retrieval-augmented generation (RAG),
coordinate multiple agents that specialize in different skills, and establish
a feedback loop for self-evaluation.

Estimated time: **75–90 minutes**  
Prerequisites: Tutorials 01–04

---

## 1. Retrieval-Augmented Generation

RAG allows an agent to ground its answers in external knowledge. Instead of
relying solely on the model’s training data, the agent retrieves relevant
documents and injects them into the prompt.

Open `tutorials/05-advanced/rag_agent.py` to explore a lightweight
implementation that keeps everything in-memory:

```python
from tutorials.05-advanced.rag_agent import InMemoryVectorStore

store = InMemoryVectorStore()
store.add_document("rag-basics", "RAG combines retrieval with generation...")
```

Key ideas:

- `InMemoryVectorStore` stores small documents and represents them using simple
  bag-of-words embeddings (no external services required).
- `RAGAgent` wraps a `BaseAgent`, retrieves top-k passages, and injects them
  into the system prompt before calling the model.
- The retrieval strategy is modular—swap it out for Pinecone, Chroma, etc.,
  once you are ready.

Run the demo:

```bash
cd tutorials/05-advanced
python rag_agent.py
```

Bring your own notes (Markdown files, transcripts) and load them into the
vector store before asking questions.

---

## 2. Multi-Agent Collaboration

Complex tasks benefit from specialized agents coordinated by an orchestrator.
`multi_agent_team.py` demonstrates a simple manager/worker architecture:

```python
from tutorials.05-advanced.multi_agent_team import AgentTeam

team = AgentTeam()
report = team.handle_request(
    "Summarize two renewable energy trends and provide a cost comparison."
)
```

How it works:

1. The **Planner Agent** breaks the goal into specialist tasks.
2. Two **Worker Agents** focus on `research` and `analysis`.
3. The **Reviewer Agent** critiques the draft and suggests improvements.
4. The orchestrator merges the feedback into a final response.

Follow the code to see how each agent reuses the shared infrastructure from
`src/agent`, `src/memory`, and `src/planning`.

---

## 3. Self-Evaluation & Feedback

Evaluation closes the loop. After generating a response, ask another agent (or
the same model with a critical mindset) to review the output. The reviewer
should check for:

- Factual errors
- Missing requirements
- Poor structure or unclear explanations

In `multi_agent_team.py`, the reviewer returns a list of issues. The manager
decides whether to accept the work or iterate. Try tweaking the threshold for
revisions or prompting the reviewer to be more/less strict.

---

## 4. Exercises

1. **Grounding with Files**  
   Extend the RAG agent to index all Markdown files in a directory. Use
   `pathlib` to discover files, read their contents, and add them to the
   vector store.

2. **Hybrid Retrieval**  
   Combine keyword filtering with cosine similarity to improve ranking. Hint:
   use `collections.Counter` and `math.sqrt` for TF-IDF-style scoring.

3. **Specialist Agents**  
   Add a `visualization` worker that outputs chart descriptions. Modify the
   planner to schedule it when the user requests graphs.

4. **Evaluation Reports**  
   Persist reviewer feedback to a JSON or Markdown report so learners can
   inspect the outcomes after each run.

---

## 5. Troubleshooting

- **No documents found**: Ensure you load documents before querying the RAG
  agent. Use `store.list_ids()` to verify what is indexed.
- **Agents disagree**: Tune each agent’s system prompt and temperature. Lower
  temperatures produce more deterministic, less chatty output.
- **Feedback loop stalls**: Limit the number of revision cycles to avoid
  infinite loops. See the `max_revisions` parameter in the agent team.

---

## 6. Next Steps

You now have:

- Memory-enhanced chat agents
- Tool-using ReAct planners
- Retrieval-augmented generation
- Multi-agent orchestration with self-evaluation

Suggested follow-ups:

- Integrate real vector databases (Chroma, Weaviate, Pinecone)
- Deploy your agent via a simple FastAPI or Gradio interface
- Instrument logging/analytics to monitor agent performance
- Explore automated agent evaluation frameworks (TruLens, LangSmith, Evals)

Congratulations—your toolbox is ready for production-scale AI agents! 🚀
