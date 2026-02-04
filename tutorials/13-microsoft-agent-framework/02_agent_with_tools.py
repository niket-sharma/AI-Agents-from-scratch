"""
Agent with Tools — Microsoft Agent Framework
=============================================

Extends an agent with three callable tools using the @tool decorator.  The
agent autonomously decides which tool to invoke — no explicit routing logic
is needed.  The LLM reads each tool's docstring to understand when and how
to call it.

Tools provided:
    get_weather(city)     – Simulated weather lookup (static data, no HTTP).
    calculate(expression) – Safe arithmetic evaluator (AST whitelist, same
                            pattern as tutorials/06-langgraph/langgraph_agent.py).
    get_current_time()    – Returns the current local date and time.

Concepts covered:
    - @tool decorator: the decorated function's docstring becomes the
      tool description sent to the LLM.
    - tools=[…] on .as_agent(): registers every tool at agent creation time.
    - Autonomous tool selection: the agent decides which tool to call and
      with what arguments; tool-call round-trips are handled internally.

Usage:
    python 02_agent_with_tools.py

Requirements:
    - OPENAI_API_KEY environment variable set
    - pip install -r requirements.txt
"""

import ast
import asyncio
import operator
import os
from datetime import datetime
from typing import Callable, Dict, Type

from dotenv import load_dotenv

from agent_framework import tool
from agent_framework.openai import OpenAIChatClient

# ============================================================================
# Environment
# ============================================================================

load_dotenv()

DEFAULT_MODEL = "gpt-4o-mini"


# ============================================================================
# Helpers
# ============================================================================


def _validate_api_key() -> None:
    """Exit with a helpful message when OPENAI_API_KEY is missing.

    Raises:
        SystemExit: If the key is not set in the environment.
    """
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set.")
        print("  1. Create a .env file with  OPENAI_API_KEY=sk-...")
        print("  2. Or export it in your shell.")
        raise SystemExit(1)


# ============================================================================
# Tool 1 — simulated weather
# ============================================================================

# Static weather data — keeps the tutorial runnable offline and focused on
# the framework rather than on network plumbing.
_WEATHER_DB: Dict[str, Dict[str, str]] = {
    "london":        {"temp": "15°C", "condition": "Cloudy",         "humidity": "72%"},
    "new york":      {"temp": "22°C", "condition": "Sunny",          "humidity": "45%"},
    "tokyo":         {"temp": "28°C", "condition": "Humid",          "humidity": "80%"},
    "paris":         {"temp": "18°C", "condition": "Partly Cloudy",  "humidity": "60%"},
    "sydney":        {"temp": "25°C", "condition": "Clear",          "humidity": "55%"},
    "san francisco": {"temp": "17°C", "condition": "Foggy",          "humidity": "68%"},
    "toronto":       {"temp": "10°C", "condition": "Rainy",          "humidity": "75%"},
    "berlin":        {"temp": "12°C", "condition": "Overcast",       "humidity": "65%"},
}


@tool
def get_weather(city: str) -> str:
    """Return the current weather for a given city.

    Supported cities: London, New York, Tokyo, Paris, Sydney,
    San Francisco, Toronto, Berlin.

    Args:
        city: Name of the city (case-insensitive).

    Returns:
        A human-readable weather summary, or an error listing available cities.
    """
    key = city.strip().lower()
    if key not in _WEATHER_DB:
        available = ", ".join(c.title() for c in _WEATHER_DB)
        return f"Weather data not available for '{city}'. Try one of: {available}"
    data = _WEATHER_DB[key]
    return (
        f"Weather in {city.title()}: {data['temp']}, "
        f"{data['condition']}, Humidity {data['humidity']}"
    )


# ============================================================================
# Tool 2 — safe arithmetic calculator
# ============================================================================

# Whitelist of binary operators permitted in expressions.
# Mirrors tutorials/06-langgraph/langgraph_agent.py exactly, with the
# addition of FloorDiv and an explicit division-by-zero guard.
_ALLOWED_OPERATORS: Dict[Type[ast.AST], Callable[[float, float], float]] = {
    ast.Add:      operator.add,
    ast.Sub:      operator.sub,
    ast.Mult:     operator.mul,
    ast.Div:      operator.truediv,
    ast.Pow:      operator.pow,
    ast.Mod:      operator.mod,
    ast.FloorDiv: operator.floordiv,
}


def _safe_eval(expression: str) -> float:
    """Evaluate an arithmetic expression using an AST node whitelist.

    Only numeric literals, basic binary operators (+, -, *, /, **, %, //),
    unary +/-, and parentheses are allowed.  No function calls, attribute
    access, or imports can slip through.

    Args:
        expression: A math expression string, e.g. "2 * (3 + 4)".

    Returns:
        The floating-point result.

    Raises:
        ValueError: If the expression contains disallowed constructs or
                    division by zero.
    """

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.BinOp):
            left  = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type not in _ALLOWED_OPERATORS:
                raise ValueError(f"Operator {op_type.__name__} is not allowed.")
            if op_type in (ast.Div, ast.FloorDiv) and right == 0:
                raise ValueError("Division by zero.")
            return _ALLOWED_OPERATORS[op_type](left, right)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            val = _eval(node.operand)
            return -val if isinstance(node.op, ast.USub) else val
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError("Only basic arithmetic expressions are supported.")

    tree = ast.parse(expression, mode="eval")
    return _eval(tree.body)


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Supports: +  -  *  /  **  %  //  and parentheses.
    No variables, function calls, or imports are permitted.

    Args:
        expression: The arithmetic expression, e.g. "(10 - 2) ** 2".

    Returns:
        The result as a string, or an error message.
    """
    try:
        result = _safe_eval(expression)
        # Show integers cleanly (no trailing .0)
        return str(int(result)) if result == int(result) else str(result)
    except Exception as exc:
        return f"Calculation error: {exc}"


# ============================================================================
# Tool 3 — current time
# ============================================================================


@tool
def get_current_time() -> str:
    """Return the current local date and time.

    Returns:
        Formatted string, e.g. "2026-02-04 14:32:07".
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================================================
# Agent factory
# ============================================================================


def _create_tool_agent():
    """Create an agent with all three tools registered.

    The instructions tell the agent when each tool is appropriate.  The
    framework automatically adds the tool schemas to the API request.

    Returns:
        A ChatAgent with get_weather, calculate, and get_current_time.
    """
    return OpenAIChatClient(model_id=DEFAULT_MODEL).as_agent(
        name="ToolAgent",
        instructions=(
            "You are a helpful assistant with access to tools. "
            "Use get_weather when the user asks about weather in a city. "
            "Use calculate when the user has a math question. "
            "Use get_current_time when the user asks about the current time or date. "
            "For anything else, answer directly."
        ),
        tools=[get_weather, calculate, get_current_time],
    )


# ============================================================================
# Demo — interactive tool-using chat
# ============================================================================


async def demo_tool_chat() -> None:
    """Interactive session where the agent autonomously picks tools.

    The agent sees all three tools at creation time and decides on every
    turn whether to call one, which one, and with what arguments.  Tool-call
    round-trips are handled inside the framework — you only see the final
    answer.

    Type 'quit', 'exit', or 'bye' to end.

    Suggested prompts to try:
        "What is the weather in Tokyo?"
        "Calculate (15 + 7) * 3"
        "What time is it right now?"
        "Tell me a fun fact."   <- no tool needed; agent answers directly
    """
    _validate_api_key()

    print("\n" + "=" * 80)
    print("  DEMO: Interactive Agent with Tools")
    print("=" * 80)
    print("\nAvailable tools: weather lookup, calculator, clock.")
    print("Type 'quit', 'exit', or 'bye' to end.\n")
    print("Suggested prompts:")
    print("  • What is the weather in London?")
    print("  • Calculate (15 + 7) * 3")
    print("  • What time is it?")
    print("  • Tell me a fun fact.\n")

    agent = _create_tool_agent()

    while True:
        try:
            user_input = input("[You] ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.lower() in ("quit", "exit", "bye", "q"):
            print("\n[ToolAgent] Goodbye!\n")
            break

        if not user_input:
            continue

        # Single-turn; the framework handles any tool-call round-trips internally
        result = await agent.run(user_input)
        print(f"[ToolAgent] {result.text}\n")


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    asyncio.run(demo_tool_chat())
