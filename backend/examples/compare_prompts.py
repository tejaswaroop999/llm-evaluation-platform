"""Synthetic comparison with real measured local latency; no model-quality claim."""
import json
from pathlib import Path
from app.db.runs import RunStore
from app.schemas import Dataset, EvaluationCase, PromptVersion
from app.services.providers.adapters import EchoProvider
from app.services.runner import execute_run


def main():
    dataset = Dataset(name="Echo contract fixtures", cases=[
        EvaluationCase(input="42", expected_output="42"),
        EvaluationCase(input="Paris", expected_output="Paris"),
        EvaluationCase(input="café", expected_output="café"),
    ])
    store = RunStore("data/demo-evaluations.db")
    comparison = []
    for version, template in [(1, "{input}"), (2, "Answer: {input}")]:
        record = execute_run(dataset, PromptVersion(name="echo-contract", version=version, template=template), EchoProvider())
        store.save(record)
        comparison.append({"run_id": str(record.run.id), "prompt_version": version,
                           "passed": record.passed_cases, "total": len(record.results),
                           "pass_rate": record.pass_rate, "mean_latency_ms": record.mean_latency_ms})
    output = {"provider": "echo", "synthetic": True, "comparison": comparison}
    Path("data").mkdir(exist_ok=True)
    Path("data/demo-comparison.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
