import pytest

from app.services.evaluators import ExactMatchEvaluator


@pytest.fixture
def evaluator() -> ExactMatchEvaluator:
    return ExactMatchEvaluator()


def test_exact_strings_pass(evaluator: ExactMatchEvaluator) -> None:
    outcome = evaluator.evaluate("The answer is 42.", "The answer is 42.")

    assert outcome.passed is True
    assert outcome.score == 1.0
    assert outcome.reason == "Actual output exactly matches expected output."


def test_different_strings_fail(evaluator: ExactMatchEvaluator) -> None:
    outcome = evaluator.evaluate("42", "43")

    assert outcome.passed is False
    assert outcome.score == 0.0
    assert outcome.reason == "Actual output does not match expected output."


def test_case_difference_fails_under_strict_mode(
    evaluator: ExactMatchEvaluator,
) -> None:
    assert evaluator.evaluate("Answer", "answer").passed is False


def test_trailing_whitespace_difference_fails_under_strict_mode(
    evaluator: ExactMatchEvaluator,
) -> None:
    assert evaluator.evaluate("answer", "answer ").passed is False


def test_empty_strings_match(evaluator: ExactMatchEvaluator) -> None:
    outcome = evaluator.evaluate("", "")

    assert outcome.passed is True
    assert outcome.score == 1.0


def test_empty_expected_and_non_empty_actual_fail(
    evaluator: ExactMatchEvaluator,
) -> None:
    assert evaluator.evaluate("", "answer").passed is False


def test_unicode_text_is_compared_without_transformation(
    evaluator: ExactMatchEvaluator,
) -> None:
        unicode_text = "caf\u00e9"
        assert evaluator.evaluate(unicode_text, unicode_text).passed is True
        assert evaluator.evaluate(unicode_text, f"{unicode_text} ").passed is False


def test_outcome_score_is_always_between_zero_and_one(
    evaluator: ExactMatchEvaluator,
) -> None:
    matching = evaluator.evaluate("same", "same")
    different = evaluator.evaluate("expected", "actual")

    assert 0 <= matching.score <= 1
    assert 0 <= different.score <= 1


def test_outcome_has_structured_result(evaluator: ExactMatchEvaluator) -> None:
    outcome = evaluator.evaluate("expected", "actual")

    assert outcome.model_dump() == {
        "passed": False,
        "score": 0.0,
        "reason": "Actual output does not match expected output.",
    }