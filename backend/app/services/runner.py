from datetime import datetime, timezone
from time import perf_counter
from app.schemas import Dataset, EvaluationRun, EvaluationResult, EvaluationRunStatus, PromptVersion
from app.schemas.runs import RunRecord
from app.services.evaluators import ExactMatchEvaluator
from app.services.providers.adapters import Provider, ProviderError


def execute_run(dataset: Dataset, prompt: PromptVersion, provider: Provider) -> RunRecord:
    if not dataset.cases:
        raise ValueError("Dataset must have at least one case")
    run = EvaluationRun(dataset_id=dataset.id, prompt_version_id=prompt.id,
                        provider=provider.name, model=provider.model,
                        evaluator_names=["exact_match"], status=EvaluationRunStatus.RUNNING)
    results = []
    evaluator = ExactMatchEvaluator()
    for case in dataset.cases:
        start = perf_counter()
        result = EvaluationResult(run_id=run.id, case_id=case.id, input=case.input,
                                  expected_output=case.expected_output)
        try:
            output = provider.generate(prompt.template.replace("{input}", case.input))
            outcome = evaluator.evaluate(case.expected_output, output.text)
            result.actual_output = output.text
            result.passed = outcome.passed
            result.score = outcome.score
            result.reason = outcome.reason
            result.input_tokens = output.input_tokens
            result.output_tokens = output.output_tokens
        except ProviderError as exc:
            result.error = str(exc)
        result.latency_ms = (perf_counter() - start) * 1000
        results.append(result)
    errors = sum(result.error is not None for result in results)
    passed = sum(result.passed is True for result in results)
    failed = sum(result.passed is False for result in results)
    run.status = EvaluationRunStatus.FAILED if errors else EvaluationRunStatus.COMPLETED
    return RunRecord(run=run, dataset=dataset.model_copy(deep=True), prompt=prompt,
                     results=results, completed_at=datetime.now(timezone.utc),
                     passed_cases=passed, failed_cases=failed, error_cases=errors,
                     pass_rate=passed / len(results),
                     mean_latency_ms=sum(result.latency_ms for result in results) / len(results))
