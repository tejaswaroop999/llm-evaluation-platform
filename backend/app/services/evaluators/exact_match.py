from app.services.evaluators.base import EvaluationOutcome


class ExactMatchEvaluator:
    """Evaluate outputs using strict, case-sensitive string equality."""

    def evaluate(self, expected: str, actual: str) -> EvaluationOutcome:
        if expected == actual:
            return EvaluationOutcome(
                passed=True,
                score=1.0,
                reason="Actual output exactly matches expected output.",
            )

        return EvaluationOutcome(
            passed=False,
            score=0.0,
            reason="Actual output does not match expected output.",
        )