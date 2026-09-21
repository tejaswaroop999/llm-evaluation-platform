from datetime import timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import Dataset, EvaluationCase, EvaluationResult, EvaluationRun


def test_dataset_contains_cases_and_uses_utc_timestamp() -> None:
    evaluation_case = EvaluationCase(
        input="What is 2 + 2?",
        expected_output="4",
    )
    dataset = Dataset(name="Arithmetic", cases=[evaluation_case])

    assert dataset.cases == [evaluation_case]
    assert dataset.created_at.tzinfo == timezone.utc


def test_evaluation_run_defaults_to_pending() -> None:
    run = EvaluationRun(
        dataset_id=uuid4(),
        prompt_version_id=uuid4(),
        provider="mock",
        model="test-model",
    )

    assert run.status == "pending"
    assert run.evaluator_names == []


def test_result_rejects_scores_outside_normalized_range() -> None:
    with pytest.raises(ValidationError):
        EvaluationResult(
            run_id=uuid4(),
            case_id=uuid4(),
            input="input",
            expected_output="expected",
            score=1.1,
        )


def test_domain_models_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        EvaluationCase(
            input="input",
            expected_output="expected",
            unexpected="value",
        )