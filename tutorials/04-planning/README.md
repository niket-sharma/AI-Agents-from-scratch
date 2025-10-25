# Tutorial 04: Planning & Reasoning Agents

In the previous tutorials you learned how to build conversational agents, add
memory, and extend them with tools. This tutorial focuses on teaching your
agent to **plan**, **reason**, and **coordinate multiple steps** when solving a
task. You will implement the ReAct pattern, break large objectives into small
actions, and combine everything into a capable reasoning agent.

---

## Learning Objectives

By the end of this tutorial you will:

- Understand when and why agents need a planning loop
- Implement the ReAct (Reason + Act) pattern from scratch
- Build a reusable planner that can call tools and aggregate observations
- Decompose complex objectives into actionable steps
- Combine planning with memory for richer context

Estimated time: **60–75 minutes**

Prerequisites:

- Tutorial 01: Simple Agent
- Tutorial 02: Memory
- Tutorial 03: Tools (or the MCP Servers module)

---

## 1. Understanding Planning Loops

Traditional chat agents respond directly to each message. Planning agents first
**reason about the problem**, decide which tool to call, interpret the result,
and only then present an answer. This creates a deliberate feedback loop:

```
Thought → Action → Observation → (repeat) → Final Answer
```

This loop is especially helpful when:

- The answer requires multiple calculations or external lookups
- You must verify intermediate results
- The agent needs to explain its reasoning
- The task should be auditable step-by-step

---

## 2. ReAct in Action

The ReAct pattern pairs natural language reasoning with tool execution. Agents
alternate between writing a **Thought** (their internal reasoning) and
producing an **Action** (calling a tool). The tool returns an **Observation**
that is appended to the context for the next turn. When the agent is ready, it
stops with `Action: Finish` and includes a `Final Answer`.

Open `tutorials/04-planning/planning_agent.py` and explore the key components:

```python
from src.agent import BaseAgent
from src.planning import ReActPlanner
from src.tools import CalculatorTool

calculator = CalculatorTool()
planner = ReActPlanner(tools=[calculator])

agent = BaseAgent(
    system_prompt="You are a thoughtful math tutor. Show your reasoning.",
)

answer, steps = planner.run(
    question="What is (42 * 1.5) + 17?",
    agent=agent,
)
```

Each `steps` entry contains `thought`, `action`, `action_input`,
`observation`, and optionally `final_answer`. Print them to inspect the agent's
reasoning.

---

## 3. Formatting Prompts for Planning

The planner builds a structured prompt that reminds the model how to respond.
Inspect `src/planning/react.py` to see how the prompt is assembled. Important
pieces include:

- A reminder of the ReAct format (`Thought:`, `Action:`, ...)
- A list of available tools with descriptions
- The question you want to solve
- The trajectory so far (previous steps)

Tip: When the model drifts away from the format, add stronger instructions or
examples to the prompt.

---

## 4. Implementing Task Decomposition

ReAct shines when paired with a high-level plan. `TaskDecomposer` in
`src/planning/task_decomposition.py` uses either a heuristic function or an LLM
call to split a goal into clear steps.

```python
from src.planning import TaskDecomposer

decomposer = TaskDecomposer()
subtasks = decomposer.decompose(
    goal="Research the market size for electric bikes and prepare a summary",
    agent=agent,
)
```

Use the resulting subtasks as inputs for individual ReAct runs, or loop through
them to orchestrate a larger workflow.

---

## 5. Bringing It Together

The `main()` function inside `planning_agent.py` demonstrates a full cycle:

1. Break a complex user request into subtasks.
2. Use the ReAct planner for each subtask.
3. Collect final answers and present a synthesized response.

Run it with:

```bash
cd tutorials/04-planning
python planning_agent.py
```

Provide a request such as:

```
Plan a weekend itinerary in Paris with a cost estimate.
```

Observe the printed steps and how the planner uses the calculator tool for the
budget portion.

---

## 6. Exercises

1. **Add More Tools**  
   Build a `SearchTool` that returns curated knowledge from a local JSON file.
   Register it with `ReActPlanner` and update the prompt to explain when to use
   it.

2. **Improve Observability**  
   Log each `Thought`/`Action`/`Observation` to a file. Try printing them as a
   table for easier debugging.

3. **Enforce Output Format**  
   Modify `_parse_step` in `ReActPlanner` to raise an error when the model skips
   required fields. Catch the error and re-prompt the model with a reminder.

4. **Sequential Plans**  
   Use `TaskDecomposer` to break down content-generation tasks (e.g.,
   "Write a study guide about transformers") and pipe each step into a ReAct
   loop that produces focused content.

---

## 7. Troubleshooting

- **Model ignores the tool**: Strengthen the instructions. Provide examples or
  mention the tool earlier in the prompt.
- **Infinite loops**: Adjust `max_steps` to something safe (default is 5) and
  inspect the final step to see why the agent never chose `Action: Finish`.
- **Observation is empty**: Ensure your tool returns a string via
  `ToolResult.content`.
- **Token limits**: Combine planning with the token-aware memory from
  Tutorial 02. Pass the same memory instance to the agent before running the
  planner.

---

## 8. Next Steps

You now have an agent capable of deliberate multi-step reasoning. Continue to
[Tutorial 05](../05-advanced/README.md) to add retrieval-augmented generation,
multi-agent collaboration, and evaluation—critical skills for production AI
agents.

---

Happy planning! 🧠⚙️
