"""
Tutorial 09 - Minimal LangChain ReAct Agent.

This script builds a LangChain agent from scratch using ChatOpenAI +
`create_react_agent`. It wires a safe calculator tool, runs a trip-planning
question, and prints the final answer.
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
    """Return the list of LangChain tools."""
    return [
        Tool(
            name="Calculator",
            func=safe_calculator,
            description="Useful for arithmetic. Input should be a math expression like '23 * 9' or '(1200/3) + 45'.",
        )
    ]


def build_prompt() -> ChatPromptTemplate:
    """Prompt template that supports ReAct style."""
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a precise research and planning assistant. "
                "Reason carefully, decide if you need a tool, and answer in a concise, actionable format.",
            ),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )


def run_agent(task: str) -> dict[str, Any]:
    """Create the LangChain agent and execute a task."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    tools = build_tools()
    prompt = build_prompt()
    agent = create_react_agent(llm, tools, prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        handle_parsing_errors=True,
        max_iterations=5,
        verbose=True,
    )
    return executor.invoke({"input": task})


def main() -> None:
    load_dotenv(override=True)
    task = (
        "Plan a 3-day trip to Tokyo on a $1200 budget. Include daytime and evening ideas "
        "plus a quick cost breakdown (use the calculator when needed)."
    )
    result = run_agent(task)

    print("\n=== Final Answer ===")
    print(result["output"])

    intermediate: Iterable[Any] = result.get("intermediate_steps", [])
    if intermediate:
        print("\n=== Tool Calls ===")
        for action, observation in intermediate:
            print(f"Tool: {action.tool}\nInput: {action.tool_input}\nObservation: {observation}\n---")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        load_dotenv(override=True)
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required.")
    main()
