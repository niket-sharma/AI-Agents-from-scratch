"""
Tutorial 09 (bonus): Multi-agent coordination with vanilla LangChain.

This script orchestrates three LangChain ReAct agents—Researcher, Coder, and Reviewer—
without LangGraph. Each agent is created with `create_react_agent`, and we pass
context manually between them to complete a structured analytics task.
"""

from __future__ import annotations

import ast
import operator
import os
from typing import Any, Iterable

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}


def safe_calculator(expression: str) -> str:
    """Evaluate a math expression safely using AST parsing."""
    if not expression.strip():
        raise ValueError("Empty expression.")

    node = ast.parse(expression, mode="eval").body

    def _eval(subnode: ast.AST) -> float:
        if isinstance(subnode, ast.Num):  # type: ignore[attr-defined]
            return float(subnode.n)
        if isinstance(subnode, ast.Constant) and isinstance(subnode.value, (int, float)):
            return float(subnode.value)
        if isinstance(subnode, ast.BinOp) and type(subnode.op) in ALLOWED_OPERATORS:
            left = _eval(subnode.left)
            right = _eval(subnode.right)
            return ALLOWED_OPERATORS[type(subnode.op)](left, right)
        if isinstance(subnode, ast.UnaryOp) and isinstance(subnode.op, (ast.UAdd, ast.USub)):
            return +_eval(subnode.operand) if isinstance(subnode.op, ast.UAdd) else -_eval(subnode.operand)
        raise ValueError("Unsupported expression.")

    return str(_eval(node))


def build_tools() -> list[Tool]:
    """Return shared tools for every agent."""
    return [
        Tool(
            name="Calculator",
            func=safe_calculator,
            description="Useful for arithmetic. Input should be a math expression like '1200/3 + 45'.",
        )
    ]


def create_agent(system_prompt: str, llm: ChatOpenAI, tools: list[Tool]) -> AgentExecutor:
    """Create a ReAct agent with a custom system prompt."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=4,
        handle_parsing_errors=True,
    )


def format_steps(result: dict[str, Any]) -> Iterable[str]:
    """Yield formatted intermediate steps for logging."""
    for action, observation in result.get("intermediate_steps", []):
        yield f"Tool: {action.tool}\nInput: {action.tool_input}\nObservation: {observation}\n---"


def run_pipeline(question: str) -> None:
    """Coordinate the three agents on the provided question."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.25)
    tools = build_tools()

    researcher = create_agent(
        "You are ResearchAgent. Read the business question, outline 3-4 bullet steps, "
        "and highlight which columns/statistics from time_series.csv you need.",
        llm,
        tools,
    )
    coder = create_agent(
        "You are CoderAgent. Write Python (pandas + matplotlib) pseudocode or code snippets "
        "that implement the given analysis plan. Emphasize data loading, cleaning, and anomaly checks. "
        "Do NOT actually run code; just produce steps.",
        llm,
        tools,
    )
    reviewer = create_agent(
        "You are ReviewerAgent. Evaluate the plan and code snippet for completeness, safety, "
        "and whether it answers the question. Respond with PASS/FAIL and reasons.",
        llm,
        tools,
    )

    context: dict[str, Any] = {}

    # Step 1: Researcher plan
    research_result = researcher.invoke(
        {
            "input": (
                f"Question: {question}\n"
                "Describe a short plan (bullets) and note which columns from time_series.csv you expect."
            )
        }
    )
    context["plan"] = research_result["output"]

    # Step 2: Coder produces pseudocode leveraging plan
    coder_result = coder.invoke(
        {
            "input": (
                f"Follow this plan:\n{context['plan']}\n\n"
                "Write Python pseudocode (pandas/matplotlib) to execute the analysis. "
                "Focus on seasonality + anomaly detection. Mention any helper functions."
            )
        }
    )
    context["code"] = coder_result["output"]

    # Step 3: Reviewer checks the work
    reviewer_result = reviewer.invoke(
        {
            "input": (
                "Review the following materials:\n"
                f"Plan:\n{context['plan']}\n\n"
                f"Code snippet:\n{context['code']}\n\n"
                "Respond with PASS or FAIL and list concrete reasons."
            )
        }
    )
    context["review"] = reviewer_result["output"]

    print("\n=== Research Agent Output ===")
    print(context["plan"])
    for step in format_steps(research_result):
        print(step)

    print("\n=== Coder Agent Output ===")
    print(context["code"])
    for step in format_steps(coder_result):
        print(step)

    print("\n=== Reviewer Agent Output ===")
    print(context["review"])
    for step in format_steps(reviewer_result):
        print(step)


def main() -> None:
    load_dotenv(override=True)
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required.")

    task = (
        "Find seasonality, anomalies, and 2 recommendations using the dataset time_series.csv. "
        "Return a punchy summary at the end."
    )
    run_pipeline(task)


if __name__ == "__main__":
    main()
