from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any, Literal


class MathToolError(ValueError):
    """Raised when the math tool receives invalid inputs."""


@dataclass
class _EvalResult:
    value: float
    operations: int
    steps: list[str]
    expression: str


def _evaluate_ast(node: ast.AST) -> _EvalResult:
    if isinstance(node, ast.Expression):
        return _evaluate_ast(node.body)

    if isinstance(node, ast.BinOp):
        left = _evaluate_ast(node.left)
        right = _evaluate_ast(node.right)
        op_type = type(node.op)
        symbol: str
        func: Any
        if op_type is ast.Add:
            func = lambda a, b: a + b
            symbol = "+"
        elif op_type is ast.Sub:
            func = lambda a, b: a - b
            symbol = "-"
        elif op_type is ast.Mult:
            func = lambda a, b: a * b
            symbol = "×"
        elif op_type is ast.Div:
            if right.value == 0:
                raise MathToolError("Division by zero is not allowed.")
            func = lambda a, b: a / b
            symbol = "÷"
        else:
            raise MathToolError(f"Unsupported operator: {op_type.__name__}")

        value = func(left.value, right.value)
        expr = ast.unparse(node)
        step = f"{ast.unparse(node.left)} {symbol} {ast.unparse(node.right)} = {value}"
        return _EvalResult(
            value=value,
            operations=left.operations + right.operations + 1,
            steps=[*left.steps, *right.steps, step],
            expression=expr,
        )

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        operand = _evaluate_ast(node.operand)
        value = operand.value if isinstance(node.op, ast.UAdd) else -operand.value
        expr = ast.unparse(node)
        return _EvalResult(
            value=value,
            operations=operand.operations,
            steps=[*operand.steps, f"{expr} = {value}"],
            expression=expr,
        )

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        value = float(node.value)
        expr = ast.unparse(node)
        return _EvalResult(value=value, operations=0, steps=[f"{expr} = {value}"], expression=expr)

    raise MathToolError(f"Unsupported expression component: {ast.dump(node)}")


def compute_basic_math(expression: str) -> dict[str, Any]:
    """Evaluate an arithmetic expression composed of +, -, *, /, and parentheses."""

    if not expression:
        raise MathToolError("Expression must be a non-empty string.")

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:  # pragma: no cover - defensive
        raise MathToolError(f"Invalid expression '{expression}'.") from exc

    result = _evaluate_ast(tree)
    return {
        "expression": result.expression,
        "result": result.value,
        "operations_count": result.operations,
        "steps": result.steps,
    }
