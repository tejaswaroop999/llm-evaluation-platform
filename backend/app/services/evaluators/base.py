from typing import Protocol

from pydantic import BaseModel, Field


class EvaluationOutcome(BaseModel):
    passed: bool
    score: float = Field(ge=0, le=1)
    reason: str


class Evaluator(Protocol):
    def evaluate(self, expected: str, actual: str) -> EvaluationOutcome:
        """Compare an expected output with an actual model output."""
