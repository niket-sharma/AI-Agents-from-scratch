"""Reference implementation for Tutorial 06: LangGraph Agents."""
from __future__ import annotations

import argparse
import ast
import operator
from dataclasses import dataclass, field
from typing import Annotated, Callable, Dict, List, Optional, Sequence, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode


class AgentState(TypedDict):
    """LangGraph state that tracks every message in the conversation."""

    messages: Annotated[List[BaseMessage], add_messages]


_ALLOWED_OPERATORS: Dict[type[ast.AST], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}


def _safe_eval(expression: str) -> float:
    """Safely evaluate arithmetic expressions used by the calculator tool."""

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type not in _ALLOWED_OPERATORS:
                raise ValueError(f"Operator {op_type.__name__} is not allowed.")
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
def calculator(expression: str) -> str:
    """Evaluate arithmetic expressions such as '2 * (3 + 4)'."""

    try:
        result = _safe_eval(expression)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        raise ValueError(f"Could not evaluate expression: {exc}") from exc
    return str(result)


def _message_text(message: BaseMessage) -> str:
    """Normalize LangChain message content into plain text."""

    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for chunk in content:
            if isinstance(chunk, dict) and chunk.get("type") == "text":
                parts.append(chunk.get("text", ""))
        return "".join(parts)
    return str(content)


@dataclass
class LangGraphChatAgent:
    """A small but fully functional LangGraph-powered chat agent."""

    system_prompt: str = (
        "You are a structured agent that decides when to use tools. "
        "Explain calculations when appropriate and keep answers concise."
    )
    model: str = "gpt-4o-mini"
    temperature: float = 0.2
    tools: Optional[Sequence] = None
    llm: ChatOpenAI = field(init=False)
    history: List[BaseMessage] = field(init=False)

    def __post_init__(self) -> None:
        load_dotenv(override=True)
        self.llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        self._tools = list(self.tools) if self.tools else [calculator]
        self._graph = self._build_graph()
        self.history = [SystemMessage(content=self.system_prompt)]

    def _build_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("call_model", self._call_model)

        if self._tools:
            tool_node = ToolNode(self._tools)
            builder.add_node("call_tools", tool_node)
            builder.add_edge("call_tools", "call_model")
            builder.add_conditional_edges(
                "call_model",
                self._route_after_model,
                {"call_tools": "call_tools", "finish": END},
            )
        else:
            builder.add_edge("call_model", END)

        builder.add_edge(START, "call_model")
        return builder.compile()

    def _call_model(self, state: AgentState) -> AgentState:
        response = self.llm.invoke(state["messages"])
        return {"messages": [response]}

    @staticmethod
    def _route_after_model(state: AgentState) -> str:
        last = state["messages"][-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            return "call_tools"
        return "finish"

    def send(self, user_input: str) -> str:
        """Send a user message and return the assistant's reply."""

        self.history.append(HumanMessage(content=user_input))
        result = self._graph.invoke({"messages": list(self.history)})
        self.history = result["messages"]
        reply = self._history_last_ai()
        return _message_text(reply) if reply else ""

    def stream(self, user_input: str) -> Iterable[str]:
        """Yield chunks of the response as the graph executes."""

        self.history.append(HumanMessage(content=user_input))
        final_state: Optional[AgentState] = None
        emitted_any = False

        for event in self._graph.stream(
            {"messages": list(self.history)},
            stream_mode="updates",
        ):
            if "__end__" in event:
                final_state = event["__end__"]
                continue

            for payload in event.values():
                messages = payload.get("messages") if isinstance(payload, dict) else None
                if not messages:
                    continue
                last = messages[-1]
                if isinstance(last, AIMessageChunk):
                    text = _message_text(last)
                elif isinstance(last, AIMessage):
                    text = _message_text(last)
                else:
                    continue
                if text:
                    emitted_any = True
                    yield text

        if final_state:
            self.history = final_state["messages"]
        else:
            self.history = self._graph.invoke({"messages": list(self.history)})["messages"]

        # If nothing was emitted (non-streaming response), send the final text once.
        if not emitted_any:
            reply = self._history_last_ai()
            if reply:
                text = _message_text(reply)
                if text:
                    yield text

    def _history_last_ai(self) -> Optional[AIMessage]:
        for message in reversed(self.history):
            if isinstance(message, AIMessage):
                return message
        return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Chat with the LangGraph tutorial agent.",
    )
    parser.add_argument(
        "--system",
        default=LangGraphChatAgent.system_prompt,
        help="System prompt to seed the conversation.",
    )
    parser.add_argument(
        "--model",
        default=LangGraphChatAgent.model,
        help="OpenAI chat model (default: gpt-4o-mini).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=LangGraphChatAgent.temperature,
        help="Sampling temperature.",
    )
    parser.add_argument(
        "--stream",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Stream tokens as they are generated.",
    )
    return parser


def run_chat(agent: LangGraphChatAgent, stream: bool) -> None:
    print("Type 'exit' or 'quit' to stop the conversation.")
    while True:
        try:
            user = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            break
        if not user:
            continue
        if user.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if stream:
            print("Agent: ", end="", flush=True)
            emitted = False
            for chunk in agent.stream(user):
                if chunk:
                    emitted = True
                    print(chunk, end="", flush=True)
            if not emitted:
                print("(no response)", end="")
            print()
        else:
            reply = agent.send(user)
            print(f"Agent: {reply}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    agent = LangGraphChatAgent(
        system_prompt=args.system,
        model=args.model,
        temperature=args.temperature,
    )
    run_chat(agent, stream=args.stream)


if __name__ == "__main__":
    main()
