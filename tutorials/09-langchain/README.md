# Tutorial 09: Build a LangChain Agent from Scratch

This tutorial shows how to build a lightweight ReAct-style agent using **LangChain Core** primitives instead of the custom framework in `src/`. You will wire `ChatOpenAI`, a custom calculator tool, and LangChain's `create_react_agent` helper to answer structured tasks.

## Prerequisites

- Python 3.11+
- `pip install -r requirements.txt` (this already includes `langchain`, `langchain-community`, and `langchain-openai`)
- `OPENAI_API_KEY` stored in `.env`

Optional: set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` if you want to view traces in LangSmith.

## Files

| File | Description |
|------|-------------|
| `simple_langchain_agent.py` | Fully working script that defines a calculator tool, constructs a ReAct agent, and runs an example task |

## What You Will Learn

1. **LangChain building blocks**: `ChatOpenAI`, tools, prompts, and structured outputs.
2. **ReAct agent creation**: Using `create_react_agent` and `AgentExecutor` directly instead of the higher-level wrappers.
3. **Tool safety**: Implement a pure-Python calculator tool to keep arithmetic offloaded from the model.
4. **Running a full example**: Invoke the agent against a trip-planning query and inspect the intermediate reasoning steps.

## Step-by-step

1. **Define your tools**  
   - Each tool is a small Python function wrapped by `langchain.agents.Tool`.
   - Keep descriptions crisp so the LLM knows when to use them.

2. **Create the prompt**  
   - Use `ChatPromptTemplate.from_messages` with explicit instructions, format, and `MessagesPlaceholder("scratchpad")` so ReAct can work.

3. **Initialize the LLM**  
   - `ChatOpenAI(model="gpt-4o-mini", temperature=0.2)` works well; swap models as needed.

4. **Combine everything into an agent**  
   - `agent = create_react_agent(llm, tools, prompt)`
   - `executor = AgentExecutor(agent=agent, tools=tools, verbose=True)`

5. **Invoke the agent**  
   ```bash
   python tutorials/09-langchain/simple_langchain_agent.py
   ```
   The script prints the final answer and a compact log of tool usage.

## Suggested Exercises

1. Add a `KnowledgeBaseTool` that reads a markdown file from `docs/`.
2. Swap in `langchain_community.tools.SerpAPITool` or an internal API client.
3. Chain two agent runs together: first gather research, then write an email.
4. Add guardrails by checking `result["intermediate_steps"]` and ensuring no tool runs longer than expected.
5. Compare this LangChain agent with the AutoGen version in `tutorials/08-autogen`—what abstractions feel easier/harder?

## Troubleshooting

- **`ValueError: OPENAI_API_KEY not found`** → confirm `.env` contains the key or export it directly.
- **`ModuleNotFoundError: langchain_openai`** → rerun `pip install -r requirements.txt`.
- **Agent loops forever** → lower `max_iterations` in `AgentExecutor` or tighten your prompt instructions.

Once you're comfortable with this base agent, you can experiment with memory, LCEL chains, or port the logic into LangGraph for more complex workflows. Have fun!
