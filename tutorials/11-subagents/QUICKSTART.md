# Subagents Quickstart

Get hierarchical agent systems running in 15 minutes! 🚀

## Prerequisites

```bash
pip install openai python-dotenv
export OPENAI_API_KEY="your-api-key"
```

## Step 1: Your First Subagent (3 min)

Create `my_subagent.py`:

```python
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
from openai import OpenAI

from src.agent import BaseAgent
from src.tools import SubagentTool

load_dotenv()
client = OpenAI()

# 1. Create a specialist agent
researcher = BaseAgent(
    system_prompt="You are a research specialist. Provide concise, factual answers.",
    client=client,
)

# 2. Wrap it as a tool
research_tool = SubagentTool(
    agent=researcher,
    name="researcher",
    description="Delegate research tasks"
)

# 3. Use it!
result = research_tool.run("What are the 3 main types of AI agents?")
print(result.content)
```

Run it:
```bash
python my_subagent.py
```

## Step 2: Parent-Child Delegation (5 min)

```python
from src.tools import SubagentManager

# Create a manager for lifecycle control
manager = SubagentManager(client=client)

# Spawn specialists dynamically
researcher = manager.spawn(
    role="researcher",
    task="Research topics thoroughly"
)
writer = manager.spawn(
    role="writer",
    task="Write engaging content"
)

print(f"Active: {manager.list_active()}")  # ['researcher', 'writer']

# Execute tasks
research = researcher.complete("What is prompt engineering?")
article = writer.complete(f"Write a brief intro based on: {research}")

print("=== RESULT ===")
print(article)

# Cleanup
manager.terminate_all()
```

## Step 3: Run the Demos (5 min)

Try the pre-built examples:

```bash
# Basic parent-child subagent
python tutorials/11-subagents/simple_subagent.py

# Agent-as-tool pattern
python tutorials/11-subagents/agent_as_tool.py

# Parallel execution (faster!)
python tutorials/11-subagents/parallel_subagents.py --compare

# Recursive decomposition
python tutorials/11-subagents/recursive_subagents.py --simple
```

## Step 4: Build Something! (2 min)

Quick challenge - create a "second opinion" system:

```python
# Spawn two analysts with different perspectives
optimist = manager.spawn("optimist", "Find positive aspects and opportunities")
pessimist = manager.spawn("pessimist", "Identify risks and potential problems")

topic = "Adopting AI agents in enterprise software"

# Get both perspectives
pro = optimist.complete(topic)
con = pessimist.complete(topic)

# Synthesize
synthesizer = BaseAgent(
    system_prompt="Balance different viewpoints into a nuanced conclusion.",
    client=client,
)
balanced = synthesizer.complete(f"PRO:\n{pro}\n\nCON:\n{con}\n\nProvide balanced view:")

print(balanced)
```

## Key Patterns

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Agent-as-Tool** | Modular composition | `SubagentTool(agent, name, desc)` |
| **Dynamic Spawning** | Unknown task requirements | `manager.spawn(role, task)` |
| **Parallel Execution** | Independent subtasks | `asyncio.gather(*subagent_coros)` |
| **Recursive Decomposition** | Complex hierarchical tasks | Agent spawns child agents |

## Next Steps

- 📖 Read the full [README.md](README.md) for detailed explanations
- 🔍 Check [SUBAGENT_PATTERNS.md](SUBAGENT_PATTERNS.md) for pattern deep-dives
- 🏋️ Try the exercises in the README

---

**Time spent: ~15 minutes** ✅
