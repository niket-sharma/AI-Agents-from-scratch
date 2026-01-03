# Subagent Patterns Deep Dive

This document explores the core patterns for building hierarchical agent systems in depth.

## Table of Contents

1. [Pattern 1: Agent as Tool](#pattern-1-agent-as-tool)
2. [Pattern 2: Dynamic Spawning](#pattern-2-dynamic-spawning)
3. [Pattern 3: Parallel Execution](#pattern-3-parallel-execution)
4. [Pattern 4: Recursive Decomposition](#pattern-4-recursive-decomposition)
5. [Pattern 5: Context Inheritance](#pattern-5-context-inheritance)
6. [Pattern 6: Result Aggregation](#pattern-6-result-aggregation)
7. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## Pattern 1: Agent as Tool

### The Core Idea

Treat specialized agents as callable tools. The parent agent can invoke a subagent exactly like it would call a calculator or search tool.

### Why It Works

```
┌─────────────────────────────────────────────────────────┐
│                   Parent Agent                          │
│                                                         │
│  Available Tools:                                       │
│  ├── calculator_tool     → Mathematical operations      │
│  ├── search_tool         → Web search                   │
│  ├── researcher_agent    → Research tasks (SUBAGENT)    │
│  └── coder_agent         → Code generation (SUBAGENT)   │
│                                                         │
│  All tools use the same interface: tool.run(input)      │
└─────────────────────────────────────────────────────────┘
```

### Implementation

```python
from src.tools import SubagentTool, BaseTool, ToolResult
from src.agent import BaseAgent

class SubagentTool(BaseTool):
    """Wraps a BaseAgent to be used as a tool."""
    
    def __init__(self, agent: BaseAgent, name: str, description: str):
        self.agent = agent
        self.name = name
        self.description = description
    
    def run(self, input_text: str) -> ToolResult:
        response = self.agent.complete(input_text)
        return ToolResult(content=response)
```

### When to Use

✅ You want modular, composable agent systems  
✅ Parent needs to choose between multiple specialists  
✅ Subagent tasks are well-defined and self-contained  

### When NOT to Use

❌ Subagent needs to ask clarifying questions  
❌ Tasks require back-and-forth dialogue  
❌ Subagent output needs immediate human review  

---

## Pattern 2: Dynamic Spawning

### The Core Idea

Instead of pre-creating subagents, spawn them on-demand based on task analysis. This is more resource-efficient and allows for task-specific configuration.

### Why It Works

```
┌─────────────────────────────────────────────────────────┐
│   Task: "Research Python and write documentation"       │
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │               Task Analyzer                      │   │
│   │                                                  │   │
│   │  Detected needs:                                 │   │
│   │  • research capability  → spawn researcher      │   │
│   │  • writing capability   → spawn writer          │   │
│   │  • code capability      → NOT needed            │   │
│   └─────────────────────────────────────────────────┘   │
│                                                         │
│              Only spawn what's needed!                  │
└─────────────────────────────────────────────────────────┘
```

### Implementation

```python
from src.tools import SubagentManager

class AdaptiveOrchestrator:
    def __init__(self, client):
        self.manager = SubagentManager(client=client)
        self.analyzer = BaseAgent(
            system_prompt="Analyze tasks and list required capabilities.",
            client=client,
        )
    
    def process(self, task: str) -> str:
        # Analyze what's needed
        analysis = self.analyzer.complete(
            f"What capabilities are needed for: {task}\n"
            "List: research, coding, writing, review, analysis"
        )
        
        # Spawn only required specialists
        if "research" in analysis.lower():
            self.manager.spawn("researcher", "Find and synthesize information")
        if "coding" in analysis.lower():
            self.manager.spawn("coder", "Write clean code")
        if "writing" in analysis.lower():
            self.manager.spawn("writer", "Create clear content")
        
        # Execute with spawned agents...
        # ...
        
        # Cleanup
        self.manager.terminate_all()
```

### Benefits

1. **Resource Efficient**: Only create agents you need
2. **Task-Specific**: Each subagent configured for its specific task
3. **Flexible**: Unknown tasks handled dynamically
4. **Clean**: Agents terminated when done

---

## Pattern 3: Parallel Execution

### The Core Idea

When subtasks are independent, run subagents concurrently to reduce total execution time.

### Why It Works

```
Sequential (7.5s total):
├── Task A ──────────────────► (2.5s)
├── Task B ──────────────────► (2.5s)  
└── Task C ──────────────────► (2.5s)

Parallel (2.5s total):
├── Task A ──────────────────►
├── Task B ──────────────────► (all 2.5s)
└── Task C ──────────────────►
                              ▲
                         All finish together
```

### Implementation

```python
import asyncio

class ParallelExecutor:
    def __init__(self, client):
        self.client = client
    
    async def run_parallel(self, tasks: list[dict]) -> list[str]:
        """Run multiple subagent tasks concurrently."""
        
        async def run_one(role: str, prompt: str) -> tuple[str, str]:
            agent = BaseAgent(
                system_prompt=f"You are a {role} specialist.",
                client=self.client,
            )
            # Run in thread pool (OpenAI client is sync)
            result = await asyncio.to_thread(agent.complete, prompt)
            return (role, result)
        
        # Create all coroutines
        coros = [
            run_one(t["role"], t["prompt"]) 
            for t in tasks
        ]
        
        # Run all concurrently
        results = await asyncio.gather(*coros)
        return results

# Usage
executor = ParallelExecutor(client)
tasks = [
    {"role": "researcher", "prompt": "Research topic A"},
    {"role": "analyst", "prompt": "Analyze topic B"},
    {"role": "writer", "prompt": "Draft topic C"},
]
results = asyncio.run(executor.run_parallel(tasks))
```

### Considerations

| Factor | Impact |
|--------|--------|
| API Rate Limits | May throttle parallel requests |
| Task Size | Small tasks have high overhead |
| Dependencies | Only parallelize independent tasks |
| Error Handling | One failure shouldn't crash all |

### Error Handling for Parallel

```python
async def run_parallel_safe(self, tasks):
    """Parallel execution with error isolation."""
    
    async def run_one_safe(task):
        try:
            return await self.run_one(task)
        except Exception as e:
            return (task["role"], f"ERROR: {e}")
    
    return await asyncio.gather(
        *[run_one_safe(t) for t in tasks],
        return_exceptions=False  # We handle errors ourselves
    )
```

---

## Pattern 4: Recursive Decomposition

### The Core Idea

Complex tasks are broken into subtasks. If a subtask is still too complex, it's further decomposed. This creates a tree of agents.

### Why It Works

```
                    "Create a web app"
                           │
          ┌────────────────┼────────────────┐
          │                │                │
     "Design UI"     "Build Backend"   "Write Tests"
          │                │
     ┌────┴────┐     ┌────┴────┐
     │         │     │         │
"Layout"  "Styles" "API"   "Database"
```

### Implementation

```python
class RecursiveAgent:
    def __init__(self, max_depth=2, current_depth=0):
        self.max_depth = max_depth
        self.current_depth = current_depth
    
    def solve(self, task: str) -> str:
        # Base case: at max depth, solve directly
        if self.current_depth >= self.max_depth:
            return self._solve_directly(task)
        
        # Try to decompose
        subtasks = self._decompose(task)
        
        # If no decomposition needed, solve directly
        if not subtasks:
            return self._solve_directly(task)
        
        # Recursive case: spawn child for each subtask
        results = []
        for subtask in subtasks:
            child = RecursiveAgent(
                max_depth=self.max_depth,
                current_depth=self.current_depth + 1
            )
            result = child.solve(subtask)
            results.append(result)
        
        # Aggregate child results
        return self._synthesize(task, results)
    
    def _decompose(self, task: str) -> list[str]:
        """Ask LLM if task should be decomposed."""
        response = self.agent.complete(
            f"Should this task be broken into subtasks? {task}\n"
            "If yes, list subtasks. If no, say 'SOLVE_DIRECTLY'"
        )
        if "SOLVE_DIRECTLY" in response:
            return []
        # Parse subtasks from response
        return self._parse_subtasks(response)
```

### Safety Guards

```python
class BoundedRecursiveAgent:
    """Recursive agent with strict limits."""
    
    def __init__(
        self,
        max_depth: int = 2,
        max_total_tasks: int = 10,
        task_timeout: float = 30.0,
    ):
        self.max_depth = max_depth
        self.max_total_tasks = max_total_tasks
        self.task_timeout = task_timeout
        self._task_count = 0
    
    def solve(self, task: str, depth: int = 0) -> str:
        # Guard 1: Depth limit
        if depth > self.max_depth:
            return self._solve_directly(task)
        
        # Guard 2: Task count limit
        self._task_count += 1
        if self._task_count > self.max_total_tasks:
            raise RuntimeError("Max tasks exceeded")
        
        # Guard 3: Limit subtasks per level
        subtasks = self._decompose(task)[:3]  # Max 3 subtasks
        
        # ... rest of implementation
```

---

## Pattern 5: Context Inheritance

### The Core Idea

Subagents need context from their parent, but not ALL context. Selective inheritance prevents context overflow and keeps subagents focused.

### Strategies

#### Strategy A: Summary Inheritance

```python
def spawn_with_summary(self, task: str):
    """Pass summarized context to subagent."""
    
    # Summarize parent's context
    summary = self.agent.complete(
        f"Summarize the key context needed for: {task}\n"
        f"Full context: {self.full_context}"
    )
    
    # Create subagent with summary
    return BaseAgent(
        system_prompt=f"""You are a specialist.
Background context: {summary}
Your task: {task}""",
        client=self.client,
    )
```

#### Strategy B: Relevant Message Selection

```python
def spawn_with_relevant_context(self, task: str, messages: list):
    """Select only relevant messages for subagent."""
    
    # Filter messages by relevance
    relevant = [
        msg for msg in messages
        if self._is_relevant(msg, task)
    ]
    
    # Limit to most recent N
    context_messages = relevant[-5:]
    
    return BaseAgent(
        system_prompt=f"Context: {context_messages}\nTask: {task}",
        client=self.client,
    )
```

#### Strategy C: Structured Context Object

```python
@dataclass
class SubagentContext:
    """Structured context for subagents."""
    parent_goal: str
    relevant_facts: list[str]
    constraints: list[str]
    output_format: str

def spawn_with_structured_context(self, task: str, context: SubagentContext):
    prompt = f"""
Parent Goal: {context.parent_goal}
Relevant Facts: {context.relevant_facts}
Constraints: {context.constraints}
Expected Output: {context.output_format}

Your Task: {task}
"""
    return BaseAgent(system_prompt=prompt, client=self.client)
```

---

## Pattern 6: Result Aggregation

### The Core Idea

Combine outputs from multiple subagents into a coherent final response.

### Strategies

#### Strategy A: LLM Synthesis

```python
def aggregate_with_llm(self, results: list[tuple[str, str]]) -> str:
    """Use LLM to synthesize subagent results."""
    
    formatted = "\n\n".join([
        f"=== {role} ===\n{result}"
        for role, result in results
    ])
    
    return self.synthesizer.complete(f"""
Synthesize these specialist outputs into a coherent response:

{formatted}

Create a unified response that:
1. Combines key insights
2. Resolves any contradictions
3. Presents a clear conclusion
""")
```

#### Strategy B: Structured Aggregation

```python
def aggregate_structured(self, results: list[dict]) -> dict:
    """Aggregate structured outputs."""
    
    aggregated = {
        "summary": "",
        "key_points": [],
        "recommendations": [],
        "risks": [],
    }
    
    for result in results:
        aggregated["key_points"].extend(result.get("points", []))
        aggregated["recommendations"].extend(result.get("recs", []))
        aggregated["risks"].extend(result.get("risks", []))
    
    # Deduplicate
    aggregated["key_points"] = list(set(aggregated["key_points"]))
    
    # Generate summary from aggregated data
    aggregated["summary"] = self._generate_summary(aggregated)
    
    return aggregated
```

#### Strategy C: Voting/Consensus

```python
def aggregate_by_consensus(self, results: list[str], question: str) -> str:
    """Find consensus among subagent responses."""
    
    # Ask LLM to identify consensus
    return self.arbiter.complete(f"""
Question: {question}

Multiple specialists provided these answers:
{results}

Identify:
1. Points of agreement (consensus)
2. Points of disagreement
3. The most likely correct answer based on consensus
""")
```

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Infinite Delegation

```python
# BAD: No depth limit
class BadRecursiveAgent:
    def solve(self, task):
        subtasks = self.decompose(task)  # Always decomposes!
        for st in subtasks:
            child = BadRecursiveAgent()  # No depth tracking
            child.solve(st)  # Infinite recursion!
```

**Fix**: Always have max_depth and check it.

### ❌ Anti-Pattern 2: Context Explosion

```python
# BAD: Passing everything to subagent
subagent.complete(f"""
Here's the entire conversation history: {huge_history}
Here's all the research: {massive_research}
Here's the full codebase: {entire_codebase}

Now do this small task: {tiny_task}
""")
```

**Fix**: Summarize or filter context before passing.

### ❌ Anti-Pattern 3: No Cleanup

```python
# BAD: Subagents left hanging
def process(self, task):
    for i in range(10):
        subagent = manager.spawn(f"worker_{i}", task)
        subagent.complete(subtask)
    # Forgot to terminate! Memory leak!
```

**Fix**: Always use `terminate_all()` or context managers.

### ❌ Anti-Pattern 4: Synchronous Parallel

```python
# BAD: Looks parallel but is sequential
results = []
for task in tasks:
    result = subagent.complete(task)  # Blocks!
    results.append(result)
```

**Fix**: Use `asyncio.gather()` for true parallelism.

### ❌ Anti-Pattern 5: Single Point of Failure

```python
# BAD: One subagent failure crashes everything
results = [subagent.complete(t) for t in tasks]  # If one fails, all fail
```

**Fix**: Wrap each subagent call in try/except.

---

## Pattern Selection Guide

| Situation | Recommended Pattern |
|-----------|-------------------|
| Modular specialists with clear interfaces | Agent as Tool |
| Unknown task requirements | Dynamic Spawning |
| Independent subtasks | Parallel Execution |
| Complex hierarchical tasks | Recursive Decomposition |
| Need to limit subagent context | Context Inheritance |
| Multiple outputs to combine | Result Aggregation |

## Combining Patterns

Real systems often combine multiple patterns:

```python
class ProductionOrchestrator:
    """Combines all patterns for production use."""
    
    def process(self, task: str) -> str:
        # Pattern 2: Dynamic spawning
        specialists = self.analyze_and_spawn(task)
        
        # Pattern 4: Recursive decomposition
        subtasks = self.decompose(task, max_depth=2)
        
        # Pattern 3: Parallel execution
        results = asyncio.run(
            self.run_parallel(specialists, subtasks)
        )
        
        # Pattern 6: Result aggregation
        return self.aggregate(results)
```

---

*For hands-on examples, see the Python files in this tutorial directory.*
