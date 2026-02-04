# Tutorial 13 — Microsoft Agent Framework

[Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) is an open-source SDK (Python + .NET) for building AI agents and multi-agent workflows. It unifies concepts from Semantic Kernel and AutoGen into a single, graph-based orchestration model.

This tutorial walks from a single-agent chat all the way up to parallel fan-out/fan-in workflows — five files, each self-contained, each building on the previous concept.

---

## What You'll Build

| Concept | What happens |
|---------|--------------|
| **Basic agent** | Create an agent, run it, stream it, have a multi-turn conversation |
| **Tools** | Give the agent three tools; it decides which one to call |
| **Sequential workflow** | Wire two agents into a linear pipeline with `WorkflowBuilder` |
| **Conditional routing** | Classify an email, then branch the graph based on the result |
| **Parallel workflow** | Fan out to three expert agents, fan in to an aggregator |

---

## Prerequisites

- Completed [Tutorial 01 — Basics](../01-basics/) (or equivalent familiarity with LLM API calls)
- `OPENAI_API_KEY` set in your environment (`.env` file or shell export)
- Python 3.10+

---

## Setup

```bash
cd tutorials/13-microsoft-agent-framework

# Install tutorial dependencies (agent-framework is a public-preview package)
pip install -r requirements.txt

# Make sure your API key is available
export OPENAI_API_KEY="sk-..."
# …or add it to a .env file in this directory
```

> **Note:** `agent-framework` is currently in **public preview**.  APIs may shift between releases.  If you hit an import error, check the [official GitHub repo](https://github.com/microsoft/agent-framework) for the latest package name and import paths.

---

## File Guide

| File | Concepts | Run command | Interactive? |
|------|----------|-------------|--------------|
| [`01_basic_agent.py`](01_basic_agent.py) | Agent creation, `run()`, `run_stream()`, multi-turn history | `python 01_basic_agent.py` | Yes — multi-turn chat loop |
| [`02_agent_with_tools.py`](02_agent_with_tools.py) | `@tool` decorator, autonomous tool selection | `python 02_agent_with_tools.py` | Yes — chat with tool calls |
| [`03_sequential_workflow.py`](03_sequential_workflow.py) | `WorkflowBuilder`, `register_agent`, `add_edge`, `@executor` | `python 03_sequential_workflow.py` | No |
| [`04_conditional_routing.py`](04_conditional_routing.py) | Pydantic `response_format`, edge predicates, branching | `python 04_conditional_routing.py` | No (uncomment `demo_spam()` for the other branch) |
| [`05_parallel_workflow.py`](05_parallel_workflow.py) | `add_fan_out_edges`, `add_fan_in_edges`, parallel execution | `python 05_parallel_workflow.py` | No |

### Suggested order

Files 01 and 02 are independent — run them in either order.  Files 03–05 share the workflow primitives (`WorkflowBuilder`, `@executor`), so do 03 first, then 04 or 05 in any order.

---

## Key Concepts

### Agents & OpenAIChatClient

An *agent* is an LLM endpoint wrapped with a name and a set of instructions (system prompt).  `OpenAIChatClient` is the thin wrapper that talks to OpenAI; `.as_agent()` turns it into a runnable agent:

```python
from agent_framework.openai import OpenAIChatClient

agent = OpenAIChatClient(model_id="gpt-4o-mini").as_agent(
    name="MyAgent",
    instructions="You are …",
)
result = await agent.run("Hello")   # result.text is the reply
```

### The `@tool` Decorator

Decorate any function with `@tool` and pass it in the `tools=[…]` list.  The function's **docstring** becomes the description the LLM uses to decide when and how to call it:

```python
from agent_framework import tool

@tool
def get_weather(city: str) -> str:
    """Return the weather for a city."""          # <-- LLM reads this
    …

agent = OpenAIChatClient(…).as_agent(tools=[get_weather], …)
```

### WorkflowBuilder & Edges

`WorkflowBuilder` is a fluent API for declaring a directed graph of agent and executor nodes.  Key methods:

| Method | What it does |
|--------|--------------|
| `register_agent(factory, name=…)` | Add an agent node (factory is a no-arg callable) |
| `register_executor(factory, name=…)` | Add a custom processing node |
| `set_start_executor(name)` | Declare the graph entry point |
| `add_edge(from, to)` | Unconditional edge |
| `add_edge(from, to, condition=fn)` | Conditional edge — `fn(response) -> bool` |
| `add_fan_out_edges(src, [targets])` | One-to-many dispatch |
| `add_fan_in_edges([sources], dst)` | Many-to-one collection (waits for all) |
| `build()` | Compile and return a runnable workflow |

### Structured Outputs with Pydantic

Pass a Pydantic `BaseModel` as `response_format` to force the LLM to return valid JSON:

```python
from pydantic import BaseModel

class MyResult(BaseModel):
    score: float
    summary: str

agent = OpenAIChatClient(…).as_agent(
    default_options={"response_format": MyResult}, …
)
# Parse: MyResult.model_validate_json(result.text)
```

This is what makes conditional routing reliable — the predicate can parse the classifier's output without guessing.

### Fan-Out and Fan-In

Fan-out replicates one input to *N* parallel nodes.  Fan-in waits for all *N* to finish, then passes their outputs as a **list** to the next node.  A lightweight combiner executor merges that list into a single prompt before handing off to an aggregator agent.  Wall-clock time ≈ max(latencies), not the sum.

---

## Exercises

1. **Add a tool** — In `02_agent_with_tools.py` add a `convert_currency(amount, from_currency, to_currency)` tool with a hard-coded rate table (USD, EUR, GBP, JPY).  Run the agent and ask it to convert $100 to EUR.

2. **Extend the sequential pipeline** — In `03_sequential_workflow.py` add a third agent ("Editor") between the Reviewer and the output collector.  The Editor rewrites the tagline incorporating the Reviewer's feedback.  Wire it in and run.

3. **Add a third routing branch** — In `04_conditional_routing.py` add a "promotions" category to `SpamClassification` (e.g., `category: str` with values `"spam"`, `"promotions"`, `"legitimate"`).  Add a third branch that drafts a "promotions" summary instead of a reply.  You'll need three edge predicates.

---

## Troubleshooting

| Problem | Likely cause & fix |
|---------|--------------------|
| `ModuleNotFoundError: No module named 'agent_framework'` | Run `pip install -r requirements.txt` (the `--pre` flag is required for preview releases) |
| `OPENAI_API_KEY` error | Make sure the key is exported or in a `.env` file in the tutorial directory |
| `RuntimeError: no running event loop` | Don't nest `asyncio.run()` calls; each demo should be the only entry point |
| Agent returns empty text | The model may have hit its token limit; try a shorter prompt or increase `max_tokens` in `default_options` |

---

## What's Next

- **Compare frameworks** — Run the same "Writer → Reviewer" scenario with [Tutorial 07 — CrewAI](../07-crewai/) or [Tutorial 08 — AutoGen](../08-autogen/) and compare the builder APIs.
- **Subagent patterns** — [Tutorial 11 — Subagents](../11-subagents/) shows how to spawn and manage child agents dynamically.
- **MCP integration** — [Tutorial 03 — MCP Servers](../03-mcp-servers/) covers the Model Context Protocol, which Agent Framework also supports natively.

---

## References

- [Microsoft Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)
- [GitHub — microsoft/agent-framework](https://github.com/microsoft/agent-framework)
- [GitHub — microsoft/Agent-Framework-Samples](https://github.com/microsoft/Agent-Framework-Samples)
- [PyPI — agent-framework](https://pypi.org/project/agent-framework/)
