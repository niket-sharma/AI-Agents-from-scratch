# Tutorial 06: LangGraph Agents from Scratch

LangGraph brings structured state machines to LLM applications. In this tutorial you will move from prompt-response loops to fully traceable agents that branch, call tools, and maintain conversational state automatically.

## Tutorial Map (Plan)

| Module | Focus | Outcome |
| --- | --- | --- |
| 1. Orientation | Core LangGraph concepts | Know how StateGraphs, nodes, and `add_messages` work |
| 2. Environment Setup | Install `langgraph` plus LangChain chat models | Local environment ready for graph builds |
| 3. Minimal Graph | Build a single-node chat graph | Understand how to invoke graphs with user messages |
| 4. Tool Routing | Add a calculator tool node with conditional edges | Agent can decide when to call tools |
| 5. Memory & Streaming | Persist conversation state + stream updates | Production-friendly interaction loop |
| 6. Practice | Guided exercises + troubleshooting | Confidence to extend graph with your own logic |

Keep this map handy—the remaining sections walk through each module step-by-step.

## Learning Objectives

By the end, you will be able to:

1. Describe the relationship between LangGraph state, nodes, and edges.
2. Implement a `TypedDict` state with message aggregation via `add_messages`.
3. Build a routed chat workflow that decides when to call tools.
4. Persist conversation memory between turns and stream graph updates.
5. Extend the tutorial code to add new nodes, tools, or branch conditions.

**Estimated time**: 60–75 minutes.

## Prerequisites

- Python 3.9+ (LangGraph officially supports 3.9–3.12 at time of writing).
- An OpenAI-compatible API key in `.env` (`OPENAI_API_KEY=...`).
- Familiarity with Tutorials 01–05 (especially planning & tools).
- Packages: `langgraph`, `langchain-core`, `langchain-openai`, `python-dotenv`.

Install or upgrade the key dependencies:

```bash
pip install --upgrade "langgraph>=0.2.20" langchain-openai langchain-core
```

## Files in This Tutorial

- `tutorials/06-langgraph/langgraph_agent.py` – the reference implementation you can run and edit.
- `tutorials/06-langgraph/README.md` – this learning guide.

## 1. Orientation: How LangGraph Works

LangGraph composes LLM applications as directed graphs. Each node is a callable that receives the current state and returns a partial update. The framework merges updates back into the global state using reducers such as `add_messages`.

```
┌─────────┐    edge     ┌──────────┐
│  START  │ ──────────▶ │ call_model│
└─────────┘             └────┬─────┘
                              │conditional
                              ▼
                        ┌──────────┐
                        │call_tools│
                        └────┬─────┘
                              │edge
                              ▼
                            ┌────┐
                            │END │
                            └────┘
```

Key concepts:

- **State** – a `TypedDict`. In this tutorial it stores `messages` (conversation history).
- **Nodes** – Python callables. We use `call_model` (LLM) and `call_tools` (calculator).
- **Edges** – direct transitions or conditional routes decided at runtime.
- **Reducers** – helper functions like `add_messages` that know how to merge updates.

## 2. Set Up the Environment

1. Confirm dependencies:
   ```bash
   pip install -r requirements.txt
   pip install "langgraph>=0.2.20"
   ```
2. Ensure `.env` contains `OPENAI_API_KEY=...`.
3. (Optional) Add `ANTHROPIC_API_KEY` if you want to swap in Claude via LangChain.

> Tip: If you run inside a notebook, restart the kernel after installing LangGraph so Pydantic types register correctly.

## 3. Build the Minimal Graph

Open `langgraph_agent.py` and find `AgentState`. It looks like:

```python
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
```

The reducer `add_messages` tells LangGraph to append new `BaseMessage` objects automatically. The `LangGraphChatAgent._build_graph` method then creates a `StateGraph`, registers the `call_model` node, and connects `START -> call_model -> END`.

Run the script without streaming to see the minimal chat loop:

```bash
python tutorials/06-langgraph/langgraph_agent.py --no-stream
```

Type a few prompts—the agent responds just like a standard chat bot, but the entire exchange flows through LangGraph, making it easy to add more structure in later steps.

## 4. Add Tool Routing

Next, study `_route_after_model` and the `ToolNode` creation:

```python
builder.add_node("call_tools", ToolNode(self.tools))
builder.add_conditional_edges(
    "call_model",
    self._route_after_model,
    {"call_tools": "call_tools", "finish": END},
)
```

`_route_after_model` inspects the latest `AIMessage`. If it contains tool calls, the graph sends control to `call_tools`; otherwise it terminates at `END`. The included `@tool`-decorated calculator demonstrates the pattern without needing extra APIs.

Try asking “What is (3 * 9) + 2?”—the agent should decide to invoke the calculator tool before replying with the final answer.

## 5. Keep Memory and Stream Updates

The class stores `self.history`, which always begins with a `SystemMessage`. Every time you send user input, it:

1. Appends a `HumanMessage`.
2. Invokes the graph with the accumulated history.
3. Replaces `self.history` with the graph’s output (preserving the conversation).

For a more dynamic experience, pass `--stream` to emit tokens as soon as they are produced:

```bash
python tutorials/06-langgraph/langgraph_agent.py --stream
```

Under the hood, `graph.stream(..., stream_mode="updates")` yields intermediate node payloads. The tutorial filters for `AIMessage` chunks and prints them incrementally, then caches the final state so the next turn continues seamlessly.

## 6. Suggested Practice

1. **Add a web-search tool** – create a stub tool that reads local markdown files or hits an API, then update `_route_after_model` to send certain intents directly to it.
2. **Add guardrails** – insert a moderation node that inspects user input before it reaches `call_model`.
3. **Add branches** – create a summarization node that triggers every 5 turns to condense history.
4. **Persist state** – connect LangGraph’s `MemorySaver` checkpointing to keep chat history even after restarting the process.
5. **Swap models** – try `gpt-4o-mini`, `gpt-4.1`, or an Anthropic model via `langchain_anthropic`.

Document your experiments inside the folder so others can follow along.

## Troubleshooting

- **`ImportError: No module named langgraph`** – reinstall with `pip install langgraph` inside your active virtualenv.
- **`ValueError: OPENAI_API_KEY not found`** – double-check `.env`, then restart your shell or IDE so `python-dotenv` can load it.
- **Graph seems stateless** – ensure you keep `self.history` between turns; resetting it each invocation produces single-turn answers only.
- **Tool not triggered** – inspect the `AIMessage.tool_calls` payload by printing the latest message when debugging. The LLM must be instructed (see `tool_prompt`) to use tools.

## Next Steps

- Revisit `tutorials/05-advanced/` and replace parts of the multi-agent script with LangGraph workflows.
- Explore LangGraph’s MCP bridge to connect this agent to external tools built in Tutorial 03B.
- Read the official [LangGraph documentation](https://langchain-ai.github.io/langgraph/) for async workflows, parallel branches, and observability.

When you are comfortable with these building blocks, you are ready to design bespoke LangGraph graphs for your own production agents.
