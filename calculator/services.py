from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Operator = Literal["add", "sub", "mul", "div"]


@dataclass
class CalculationResult:
    value: float | None
    error: str | None = None


def _to_float(raw: str, field_name: str) -> tuple[float | None, str | None]:
    cleaned = (raw or "").strip()
    if not cleaned:
        return None, f"{field_name} is required."

    try:
        return float(cleaned), None
    except ValueError:
        return None, f"{field_name} must be a number."


def calculate(a_raw: str, b_raw: str, op: Operator) -> CalculationResult:
    a, error_a = _to_float(a_raw, "First number")
    if error_a:
        return CalculationResult(value=None, error=error_a)

    b, error_b = _to_float(b_raw, "Second number")
    if error_b:
        return CalculationResult(value=None, error=error_b)

    if op == "add":
        return CalculationResult(value=a + b)
    if op == "sub":
        return CalculationResult(value=a - b)
    if op == "mul":
        return CalculationResult(value=a * b)
    if op == "div":
        if b == 0:
            return CalculationResult(value=None, error="Cannot divide by zero.")
        return CalculationResult(value=a / b)

    return CalculationResult(value=None, error="Unsupported operation.")

