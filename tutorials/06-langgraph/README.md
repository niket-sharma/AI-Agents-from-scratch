# Tutorial 06: LangGraph Agents from Scratch

> **📋 New? Start here:** [INDEX.md](INDEX.md) - Complete navigation guide for this tutorial

LangGraph brings structured state machines to LLM applications. In this tutorial you will move from prompt-response loops to fully traceable agents that branch, call tools, and maintain conversational state automatically.

## 🆕 Enhanced Tutorial: Real-World Application

This tutorial now includes **two implementations**:

1. **`langgraph_agent.py`** - Basic LangGraph agent with calculator tool (original)
2. **`customer_support_agent.py`** - **NEW!** Production-ready customer support system

The customer support example showcases **why LangGraph excels**:
- ✅ **Orchestration**: Multi-stage workflow (analyze → route → handle → escalate)
- ✅ **Persistence**: Ticket state tracked throughout the conversation
- ✅ **Branching**: Automatic escalation based on priority and keywords
- ✅ **Real-world**: Practical example everyone can understand

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

| File | Purpose | Start Here? |
|------|---------|-------------|
| **`QUICKSTART.md`** | 15-minute hands-on guide | ⭐ **YES - Start here!** |
| **`customer_support_agent.py`** | Production-ready support system example | ⭐ **Run this first!** |
| **`langgraph_agent.py`** | Basic agent with calculator tool | Good for understanding basics |
| **`README.md`** | Comprehensive tutorial (this file) | Deep dive reference |
| **`COMPARISON.md`** | When to use LangGraph vs alternatives | Decision guide |

**Recommended Learning Path:**
1. Read [QUICKSTART.md](QUICKSTART.md) (15 min)
2. Run `customer_support_agent.py --mode examples` (5 min)
3. Read this README for deep understanding (45 min)
4. Check [COMPARISON.md](COMPARISON.md) when deciding if LangGraph fits your use case

## 🚀 Quick Start - Try the New Example!

```bash
# Run the customer support examples
python tutorials/06-langgraph/customer_support_agent.py --mode examples

# Or try interactive mode
python tutorials/06-langgraph/customer_support_agent.py --mode interactive
```

**What makes this example great for learning:**

1. **Concrete use case**: Customer support is familiar to everyone
2. **Clear state**: You can see ticket properties evolve (category, priority, assignment)
3. **Visible branching**: Watch urgent tickets take a different path
4. **Multiple nodes**: Each stage (analyze, route, handle, escalate) is isolated and testable
5. **Production patterns**: Built with real-world best practices

## 📊 Detailed Walkthrough: Customer Support Agent

### The Workflow Graph

```
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌──────────┐     Step 1: Analyze incoming request
│ analyze  │     - Classify category (technical/billing/account)
└────┬─────┘     - Determine priority (low/medium/high/urgent)
     │           - Generate ticket summary
     ▼
┌──────────┐     Step 2: Route to appropriate team
│  route   │     - Assign to Tech/Billing/Account/General
└────┬─────┘     - Add routing notification
     │
     ▼
┌──────────┐     Step 3: Handle the request
│  handle  │     - Search knowledge base
└────┬─────┘     - Check account status
     │           - Provide solution
     ▼
┌──────────────┐ Step 4: Check if escalation needed
│check_escalate│ - Auto-escalate urgent tickets
└───────┬──────┘ - Detect escalation keywords
        │
        ▼
   ┌─────────┐
   │conditional│
   └────┬────┘
        │
        ├─── escalate ──▶ END
        │
        └─── complete ──▶ END
```

### Key Learning Points

#### 1. **Rich State Management**

Unlike simple chat agents, this maintains structured state:

```python
class SupportAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]  # Conversation
    ticket: TicketState  # Business logic state!
```

The `ticket` field tracks:
- Category, priority, summary
- Assignment and resolution
- Timestamp and ticket ID

**Why this matters**: Real applications need more than just chat history. LangGraph lets you maintain complex domain state alongside messages.

#### 2. **Multi-Stage Orchestration**

Four specialized nodes, each with a single responsibility:

- **`analyze_ticket_node`**: Uses LLM to classify the request
- **`route_ticket_node`**: Assigns to appropriate team
- **`handle_support_node`**: Provides actual support with tools
- **`check_escalation_node`**: Determines next steps

**Why this matters**: Breaking logic into nodes makes testing, debugging, and iteration much easier. Each node can be developed and tested independently.

#### 3. **Conditional Branching**

The `should_escalate` function demonstrates clean branching logic:

```python
def should_escalate(state: SupportAgentState) -> Literal["escalate", "complete"]:
    priority = state["ticket"].get("priority", "medium")

    if priority == "urgent":
        return "escalate"

    # Check for escalation keywords
    last_message = state["messages"][-1].content
    if any(kw in last_message.lower() for kw in ["speak to manager", "lawsuit"]):
        return "escalate"

    return "complete"
```

**Why this matters**: Business logic determines the path. This is where LangGraph shines over simple prompt chains.

#### 4. **Tool Integration**

The `handle_support_node` uses tools contextually:

- `search_knowledge_base`: Find solutions to common problems
- `check_account_status`: Verify user account details
- `create_escalation`: Trigger human handoff

**Why this matters**: Tools are invoked at the right stage of the workflow, not randomly. The graph structure ensures proper sequencing.

### Example Scenarios

The tutorial includes 4 scenarios that demonstrate different paths:

1. **Low Priority** → General routing → Knowledge base solution
2. **Medium Priority** → Technical routing → Troubleshooting steps
3. **High Priority** → Billing routing → Detailed investigation
4. **Urgent** → Any routing → **Automatic escalation** 🚨

Run `python customer_support_agent.py --mode examples` to see all four!

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

### For the Basic Agent (`langgraph_agent.py`)

1. **Add a web-search tool** – create a stub tool that reads local markdown files or hits an API, then update `_route_after_model` to send certain intents directly to it.
2. **Add guardrails** – insert a moderation node that inspects user input before it reaches `call_model`.
3. **Add branches** – create a summarization node that triggers every 5 turns to condense history.
4. **Persist state** – connect LangGraph's `MemorySaver` checkpointing to keep chat history even after restarting the process.
5. **Swap models** – try `gpt-4o-mini`, `gpt-4.1`, or an Anthropic model via `langchain_anthropic`.

### For the Customer Support Agent (`customer_support_agent.py`)

**Beginner Exercises:**

1. **Add a new category** – Add "refund" as a ticket category with its own routing
2. **Expand knowledge base** – Add more Q&A pairs to `search_knowledge_base`
3. **Track metrics** – Count how many tickets of each category are processed
4. **Add timestamps** – Show how long each stage takes

**Intermediate Exercises:**

1. **Multi-turn conversations** – Modify to handle follow-up questions on the same ticket
2. **Sentiment analysis** – Add a node that detects frustrated users and adjusts priority
3. **Feedback loop** – After resolution, ask for satisfaction rating
4. **Parallel tools** – Allow `handle_support_node` to call multiple tools simultaneously

**Advanced Exercises:**

1. **Human-in-the-loop** – Add a node that waits for human approval before escalation
2. **Memory saver** – Use LangGraph's checkpointing to persist tickets to a database
3. **Sub-graphs** – Create separate sub-graphs for technical vs billing support
4. **Streaming UI** – Build a web interface that shows ticket state updating in real-time
5. **Multi-agent** – Have specialized agents for each category that the router delegates to

Document your experiments inside the folder so others can follow along.

## 🎯 When to Use LangGraph vs Other Approaches

### Use LangGraph When You Need:

✅ **Multi-step workflows** with clear stages (analyze → route → handle)
✅ **Conditional branching** based on state (urgent tickets take different paths)
✅ **Persistence** of complex state (ticket metadata, not just messages)
✅ **Observability** - you want to see which node is executing
✅ **Testability** - nodes can be unit tested independently
✅ **Human-in-the-loop** - some stages need approval

### Use Simpler Approaches When:

❌ Single LLM call is sufficient (just use chat completion API)
❌ Simple tool calling (use function calling directly)
❌ Linear prompt chains (use LangChain LCEL)
❌ No state beyond conversation history

### Comparison: Support Agent Without LangGraph

Here's what the same functionality looks like **without** LangGraph:

```python
def handle_support_messy(user_request: str):
    # Everything in one giant function - hard to test/maintain!

    # Analyze
    analysis = llm.invoke(f"Classify this: {user_request}")
    category = extract_category(analysis)
    priority = extract_priority(analysis)

    # Route
    if category == "technical":
        team = "Tech"
    elif category == "billing":
        team = "Billing"
    # ... more if/else

    # Handle
    if "password" in user_request:
        kb_result = search_kb("password")
    # ... more if/else

    # Escalate?
    if priority == "urgent":
        escalate(user_request)
        return "Escalated"

    # Generate response
    response = llm.invoke(f"Respond to: {user_request} with {kb_result}")

    return response
```

**Problems:**
- All logic tangled together
- Hard to test individual stages
- No visibility into state transitions
- Difficult to add human approval steps
- Can't easily persist or replay

**LangGraph solves all of these!**

## Troubleshooting

- **`ImportError: No module named langgraph`** – reinstall with `pip install langgraph` inside your active virtualenv.
- **`ValueError: OPENAI_API_KEY not found`** – double-check `.env`, then restart your shell or IDE so `python-dotenv` can load it.
- **Graph seems stateless** – ensure you keep `self.history` between turns; resetting it each invocation produces single-turn answers only.
- **Tool not triggered** – inspect the `AIMessage.tool_calls` payload by printing the latest message when debugging. The LLM must be instructed (see `tool_prompt`) to use tools.

## Next Steps

### Immediate Next Steps

1. **Run both examples**:
   ```bash
   # Basic agent
   python tutorials/06-langgraph/langgraph_agent.py --stream

   # Customer support agent
   python tutorials/06-langgraph/customer_support_agent.py --mode examples
   ```

2. **Modify the customer support agent**:
   - Add a new ticket category (e.g., "feature_request")
   - Implement a "satisfaction_survey" node that runs after resolution
   - Add more realistic tools (database lookup, API calls, etc.)

3. **Visualize the graph**:
   ```python
   from langgraph.graph import StateGraph
   from IPython.display import Image, display

   # In customer_support_agent.py
   agent = CustomerSupportAgent()
   display(Image(agent.graph.get_graph().draw_mermaid_png()))
   ```

### Integration with Other Tutorials

- **Tutorial 03B (MCP)**: Connect the support agent to MCP tools for real data access
- **Tutorial 05 (Advanced)**: Replace multi-agent coordination with LangGraph workflows
- **Tutorial 04 (Async)**: Add async node execution for parallel tool calls

### Deep Dive Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) - Official docs
- [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/) - More examples
- [State Management](https://langchain-ai.github.io/langgraph/concepts/low_level/#state) - Deep dive into state
- [Checkpointing](https://langchain-ai.github.io/langgraph/how-tos/persistence/) - Persist state to disk/DB

### Production Considerations

When you're ready to deploy:

1. **Add checkpointing** for crash recovery
2. **Implement proper error handling** in each node
3. **Add logging** and observability (LangSmith integration)
4. **Use async nodes** for I/O-bound operations
5. **Add rate limiting** on LLM calls
6. **Implement retries** for transient failures
7. **Add metrics** (latency, success rate, escalation rate)

When you are comfortable with these building blocks, you are ready to design bespoke LangGraph graphs for your own production agents.

## 📚 Summary

**What You Learned:**

- ✅ LangGraph state management with `TypedDict` and reducers
- ✅ Building multi-node workflows with clear separation of concerns
- ✅ Conditional edges for dynamic routing
- ✅ Maintaining complex domain state alongside messages
- ✅ When to use LangGraph vs simpler approaches

**Key Takeaway:** LangGraph excels when you need **orchestration**, **persistence**, and **branching**. For simple Q&A, stick with basic chat completions. For complex workflows, LangGraph provides the structure you need.

**Next:** Build your own LangGraph application using the customer support agent as a template!
