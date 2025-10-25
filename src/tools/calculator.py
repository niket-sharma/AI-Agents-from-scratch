from __future__ import annotations

import ast
import operator
from typing import Any, Dict

from src.tools.base import BaseTool, ToolResult


_SAFE_OPERATORS: Dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
}


class CalculatorTool(BaseTool):
    """Safe arithmetic calculator using Python's AST."""

    name = "calculator"
    description = (
        "Evaluate basic math expressions. Supports +, -, *, /, **, and parentheses."
    )

    def _eval(self, node: ast.AST) -> float:
        if isinstance(node, ast.Num):  # type: ignore[attr-defined]
            return float(node.n)  # type: ignore[attr-defined]
        if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPERATORS:
            return _SAFE_OPERATORS[type(node.op)](self._eval(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPERATORS:
            left = self._eval(node.left)
            right = self._eval(node.right)
            return _SAFE_OPERATORS[type(node.op)](left, right)
        raise ValueError("Unsupported expression")

    def run(self, input_text: str) -> ToolResult:
        try:
            tree = ast.parse(input_text, mode="eval")
            result = self._eval(tree.body)  # type: ignore[arg-type]
            return ToolResult(content=str(result))
        except Exception as exc:
            return ToolResult(content=f"Calculation error: {exc}")
