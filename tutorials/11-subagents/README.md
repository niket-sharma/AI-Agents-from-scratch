# Tutorial 11: Subagents - Hierarchical Agent Systems

## What You'll Build

In this tutorial, you'll learn to create **hierarchical agent systems** where parent agents delegate tasks to specialized child agents (subagents). This pattern enables:

- **Modular agent composition** - Build complex systems from simple, focused agents
- **Dynamic task delegation** - Parent agents spawn workers based on task analysis
- **Parallel execution** - Run multiple subagents concurrently for performance
- **Recursive decomposition** - Break complex tasks into manageable subtasks

By the end, you'll be able to build an orchestrator that dynamically manages a team of specialized subagents.

## Learning Objectives

After completing this tutorial, you will be able to:

1. **Understand** when to use subagents vs. single agents vs. peer collaboration
2. **Implement** the Agent-as-Tool pattern to compose modular agent systems
3. **Create** a parent agent that dynamically spawns specialized subagents
4. **Execute** subagents in parallel for improved performance
5. **Build** recursive agents that decompose complex tasks hierarchically
6. **Manage** subagent lifecycle (spawn, execute, terminate)
7. **Aggregate** results from multiple subagents into coherent outputs

## Prerequisites

Before starting this tutorial, you should have completed:

- ✅ **Tutorial 01-03**: Basic agents, memory, and tools
- ✅ **Tutorial 04**: Planning and ReAct pattern
- ✅ **Tutorial 05**: Multi-agent collaboration basics

Required setup:
```bash
pip install openai python-dotenv
export OPENAI_API_KEY="your-api-key"
```

## Time Required

⏱️ **60-90 minutes** for the full tutorial  
⏱️ **15 minutes** for the [QUICKSTART.md](QUICKSTART.md)

---

## Table of Contents

1. [Understanding Subagents](#1-understanding-subagents)
2. [The Agent-as-Tool Pattern](#2-the-agent-as-tool-pattern)
3. [Dynamic Subagent Spawning](#3-dynamic-subagent-spawning)
4. [Parallel Subagent Execution](#4-parallel-subagent-execution)
5. [Recursive Decomposition](#5-recursive-decomposition)
6. [Best Practices](#6-best-practices)
7. [Exercises](#7-exercises)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Understanding Subagents

### What Are Subagents?

**Subagents** are child agents created and managed by a parent (orchestrator) agent. Unlike peer-to-peer multi-agent systems where agents collaborate as equals, subagent systems have a clear hierarchy:

```
                    ┌─────────────────┐
                    │   Orchestrator  │
                    │  (Parent Agent) │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌────────────┐    ┌────────────┐    ┌────────────┐
    │ Researcher │    │   Writer   │    │  Reviewer  │
    │ (Subagent) │    │ (Subagent) │    │ (Subagent) │
    └────────────┘    └────────────┘    └────────────┘
```

### When to Use Subagents

| Scenario | Use Subagents? | Reason |
|----------|----------------|--------|
| Complex task requiring multiple specializations | ✅ Yes | Delegate to specialists |
| Tasks that can run independently | ✅ Yes | Parallel execution |
| Hierarchical decomposition needed | ✅ Yes | Recursive subagents |
| Simple, single-domain task | ❌ No | Single agent is sufficient |
| Agents need to negotiate/debate | ❌ No | Use peer collaboration |
| Real-time back-and-forth required | ❌ No | Subagents work independently |

### Subagents vs. Multi-Agent Collaboration

| Aspect | Subagents (Hierarchical) | Multi-Agent (Peer) |
|--------|-------------------------|-------------------|
| Control | Parent controls children | Agents are equals |
| Communication | Parent ↔ Children only | Any agent ↔ Any agent |
| Lifecycle | Parent spawns/terminates | Agents exist independently |
| Context | Parent provides context | Shared context |
| Best for | Task delegation | Discussion/negotiation |

---

## 2. The Agent-as-Tool Pattern

The most powerful subagent pattern treats agents as **callable tools**. The parent agent can invoke a subagent just like any other tool.

### SubagentTool Class

We've added `SubagentTool` to the framework:

```python
from src.tools import SubagentTool

# Create a specialist agent
researcher = BaseAgent(
    system_prompt="You are a research specialist..."
)

# Wrap it as a tool
research_tool = SubagentTool(
    agent=researcher,
    name="research_agent",
    description="Delegate research tasks to a specialist"
)

# Parent can now use it like any tool
result = research_tool.run("Research the history of AI agents")
print(result.content)
```

### Why This Pattern Works

1. **Consistent Interface**: Subagents use the same `run()` interface as other tools
2. **Composability**: Mix subagents with regular tools freely
3. **Discoverability**: Parent sees subagents in its tool list with descriptions
4. **Encapsulation**: Subagent complexity is hidden behind a simple interface

### Complete Example

See [agent_as_tool.py](agent_as_tool.py) for a full implementation with:
- Multiple specialist subagents (code review, documentation, testing)
- An orchestrator that chooses which specialist to invoke
- Result synthesis from multiple subagents

```bash
python agent_as_tool.py
python agent_as_tool.py --interactive  # Interactive mode
python agent_as_tool.py --chain        # Tool chaining demo
```

---

## 3. Dynamic Subagent Spawning

Instead of pre-creating subagents, the parent can spawn them dynamically based on task analysis.

### SubagentManager

The `SubagentManager` class handles the lifecycle of subagents:

```python
from src.tools import SubagentManager

# Create a manager with shared client (efficient)
manager = SubagentManager(client=openai_client)

# Spawn specialized subagents dynamically
researcher = manager.spawn(
    role="researcher",
    task="Research AI agent architectures",
)

writer = manager.spawn(
    role="writer", 
    task="Write technical documentation",
)

# Use the subagents
research = researcher.complete("What are the main AI agent patterns?")
docs = writer.complete(f"Document these patterns: {research}")

# Clean up when done
manager.terminate_all()
```

### Dynamic Spawning Based on Task

```python
def analyze_and_spawn(task: str, manager: SubagentManager):
    """Analyze a task and spawn appropriate subagents."""
    
    # Analyze what skills are needed
    if "research" in task.lower():
        manager.spawn("researcher", "Find and synthesize information")
    
    if "code" in task.lower() or "implement" in task.lower():
        manager.spawn("coder", "Write clean, tested code")
    
    if "review" in task.lower():
        manager.spawn("reviewer", "Review for quality and correctness")
    
    return manager.list_active()
```

### Complete Example

See [simple_subagent.py](simple_subagent.py) for demonstrations of:
- Creating and managing subagent lifecycles
- Parent-child context flow
- Result aggregation

```bash
python simple_subagent.py
python simple_subagent.py --interactive  # Interactive mode
```

---

## 4. Parallel Subagent Execution

When subtasks are independent, running subagents in parallel can significantly improve performance.

### Using asyncio for Parallel Execution

```python
import asyncio
from openai import OpenAI

async def run_subagents_parallel(tasks: list) -> list:
    """Run multiple subagent tasks concurrently."""
    
    async def run_one(role: str, prompt: str):
        subagent = BaseAgent(system_prompt=f"You are a {role}...")
        # Run in thread pool (OpenAI client is synchronous)
        result = await asyncio.to_thread(subagent.complete, prompt)
        return (role, result)
    
    # Create coroutines for all tasks
    coros = [run_one(t["role"], t["prompt"]) for t in tasks]
    
    # Run all concurrently
    results = await asyncio.gather(*coros)
    return results

# Usage
tasks = [
    {"role": "tech_researcher", "prompt": "Research Python async patterns"},
    {"role": "market_analyst", "prompt": "Analyze async library adoption"},
    {"role": "writer", "prompt": "Write intro to async programming"},
]

results = asyncio.run(run_subagents_parallel(tasks))
```

### Performance Comparison

Sequential execution:
```
Task 1: 2.5s
Task 2: 2.3s  
Task 3: 2.8s
Total: 7.6s
```

Parallel execution:
```
Task 1: 2.5s ─┐
Task 2: 2.3s ─┼─ All run simultaneously
Task 3: 2.8s ─┘
Total: ~2.8s (limited by slowest task)
```

### Complete Example

See [parallel_subagents.py](parallel_subagents.py) for:
- Parallel execution implementation
- Sequential vs. parallel performance comparison
- Progress tracking for parallel tasks

```bash
python parallel_subagents.py
python parallel_subagents.py --compare   # Compare seq vs parallel
python parallel_subagents.py --progress  # Progress tracking demo
```

---

## 5. Recursive Decomposition

For very complex tasks, subagents can spawn their own subagents, creating a tree of agents.

### The Pattern

```
                         ┌─────────────┐
                         │    Root     │
                         │   Agent     │
                         └──────┬──────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
       ┌────────────┐    ┌────────────┐    ┌────────────┐
       │ Subtask 1  │    │ Subtask 2  │    │ Subtask 3  │
       └─────┬──────┘    └────────────┘    └─────┬──────┘
             │                                    │
        ┌────┴────┐                          ┌────┴────┐
        │         │                          │         │
        ▼         ▼                          ▼         ▼
    ┌───────┐ ┌───────┐                  ┌───────┐ ┌───────┐
    │Sub 1a │ │Sub 1b │                  │Sub 3a │ │Sub 3b │
    └───────┘ └───────┘                  └───────┘ └───────┘
```

### Recursive Agent Implementation

```python
class RecursiveAgent:
    def __init__(self, max_depth: int = 2, current_depth: int = 0):
        self.max_depth = max_depth
        self.current_depth = current_depth
    
    def solve(self, task: str) -> str:
        # Check if at max depth
        if self.current_depth >= self.max_depth:
            return self._solve_directly(task)
        
        # Analyze if decomposition is needed
        subtasks = self._decompose(task)
        
        if not subtasks:
            return self._solve_directly(task)
        
        # Spawn child agents for each subtask
        results = []
        for subtask in subtasks:
            child = RecursiveAgent(
                max_depth=self.max_depth,
                current_depth=self.current_depth + 1,
            )
            result = child.solve(subtask)
            results.append(result)
        
        # Aggregate results
        return self._synthesize(results)
```

### Preventing Infinite Recursion

Key safeguards:
1. **Max depth limit**: Hard cap on recursion depth
2. **Max task count**: Limit total tasks across all levels
3. **Decomposition threshold**: Only decompose if task is complex enough
4. **Timeout**: Per-task time limits

### Complete Example

See [recursive_subagents.py](recursive_subagents.py) for:
- Full recursive agent implementation
- Task tree visualization
- Bounded recursive execution with safeguards

```bash
python recursive_subagents.py
python recursive_subagents.py --depth 3  # Deeper recursion
python recursive_subagents.py --simple   # Simple demo
```

---

## 6. Best Practices

### Context Management

**DO**: Pass only relevant context to subagents
```python
# Good: Selective context
subagent = manager.spawn(
    role="coder",
    task=f"Implement based on these requirements: {requirements}",
)
```

**DON'T**: Dump entire parent context
```python
# Bad: Context overload
subagent.complete(f"Here's everything: {huge_context}. Now do {small_task}")
```

### Error Handling

```python
def safe_subagent_execution(subagent, task: str) -> str:
    """Execute subagent with error handling."""
    try:
        return subagent.complete(task)
    except Exception as e:
        # Log error but don't crash parent
        logger.error(f"Subagent failed: {e}")
        return f"[Subagent error: {e}. Parent will handle.]"
```

### Resource Management

```python
# Always clean up subagents
manager = SubagentManager(client=client)
try:
    # ... use subagents ...
finally:
    manager.terminate_all()  # Cleanup even on error
```

### When NOT to Use Deep Hierarchies

- Tasks that need rapid back-and-forth communication
- Simple tasks (overhead exceeds benefit)
- When results need human review at each level
- When context must be preserved across the hierarchy

---

## 7. Exercises

### Exercise 1: Build a Code Pipeline

Create a pipeline that uses subagents for:
1. **Analyzer**: Analyze requirements and create a design
2. **Coder**: Implement the code based on design
3. **Tester**: Create tests for the implementation
4. **Reviewer**: Review everything and suggest improvements

Chain these subagents so each uses the output of the previous.

### Exercise 2: Parallel Research Aggregator

Build a research system that:
1. Takes a topic (e.g., "electric vehicles")
2. Spawns 3 parallel subagents researching different aspects:
   - Technology trends
   - Market analysis
   - Environmental impact
3. Aggregates results into a comprehensive report

Compare sequential vs. parallel execution times.

### Exercise 3: Recursive Document Summarizer

Create a recursive agent that can summarize long documents:
1. If document is short enough, summarize directly
2. If too long, split into sections
3. Spawn subagents to summarize each section
4. Synthesize section summaries into final summary
5. Implement depth limit to prevent infinite recursion

### Exercise 4: Adaptive Specialist Selection

Modify the orchestrator to:
1. Analyze incoming tasks automatically
2. Dynamically decide which specialists are needed
3. Spawn only the required specialists
4. Handle cases where no specialist is needed

---

## 8. Troubleshooting

### "Subagent responses are too generic"

**Problem**: Subagents don't have enough context.

**Solution**: Provide specific context in the system prompt or task:
```python
subagent = manager.spawn(
    role="coder",
    task="Write Python code",
    system_prompt_template="""You are a Python coder.
Project context: We're building an AI agent framework.
Style: Follow PEP 8, use type hints, write docstrings.
Task: {task}"""
)
```

### "Parallel execution isn't faster"

**Problem**: Tasks are too small or API is rate-limited.

**Solutions**:
1. Batch small tasks into fewer subagents
2. Check API rate limits
3. Ensure tasks are actually independent

### "Recursive agent never terminates"

**Problem**: Decomposition creates too many subtasks.

**Solutions**:
1. Lower `max_depth` setting
2. Add `max_total_tasks` limit
3. Make decomposition criteria stricter
4. Add timeouts per task

### "Out of context length"

**Problem**: Too much context passed between levels.

**Solution**: Summarize or filter context before passing:
```python
# Summarize before passing to subagent
summary = parent.complete(f"Summarize key points: {long_context}")
result = subagent.complete(f"Based on: {summary}\nTask: {task}")
```

---

## Next Steps

Congratulations! You've learned to build hierarchical agent systems with subagents. 

**Continue your learning:**
- **Tutorial 05**: Multi-agent collaboration (peer patterns)
- **Tutorial 06**: LangGraph for complex workflows
- **Tutorial 07**: CrewAI for team-based agents

**Try building:**
- A customer support system with escalation subagents
- An automated code review pipeline
- A research assistant with parallel fact-checking

---

## Files in This Tutorial

| File | Description |
|------|-------------|
| [README.md](README.md) | This tutorial guide |
| [QUICKSTART.md](QUICKSTART.md) | 15-minute quick start |
| [SUBAGENT_PATTERNS.md](SUBAGENT_PATTERNS.md) | Deep dive on patterns |
| [simple_subagent.py](simple_subagent.py) | Basic parent-child demo |
| [agent_as_tool.py](agent_as_tool.py) | Agent-as-tool pattern |
| [parallel_subagents.py](parallel_subagents.py) | Parallel execution |
| [recursive_subagents.py](recursive_subagents.py) | Recursive decomposition |
