from uuid import UUID, uuid4
import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.routes.runs import get_run_store
from app.db.runs import RunStore
from app.schemas import Dataset, EvaluationCase, PromptVersion
from app.services.datasets import dataset_store
from app.services.providers.adapters import EchoProvider, AnthropicProvider, ProviderError
from app.services.runner import execute_run


@pytest.fixture
def client(tmp_path):
    store = RunStore(str(tmp_path / "runs.db"))
    app.dependency_overrides[get_run_store] = lambda: store
    dataset_store.clear()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    dataset_store.clear()


def test_api_runs_compare_versions_and_survive_store_restart(client, tmp_path):
    dataset = client.post("/datasets", json={"name": "fixture", "cases": [{"input": "42", "expected_output": "42"}]}).json()
    first = client.post("/runs", json={"dataset_id": dataset["id"]})
    assert first.status_code == 201
    record = first.json()
    assert record["pass_rate"] == 1
    assert record["results"][0]["latency_ms"] >= 0
    assert record["results"][0]["estimated_cost"] is None
    second = client.post("/runs", json={"dataset_id": dataset["id"], "prompt_version": 2, "prompt_template": "Answer: {input}"}).json()
    assert second["pass_rate"] == 0
    assert second["run"]["status"] == "completed"  # evaluator failures are not infrastructure failures
    run_id = record["run"]["id"]
    assert client.get(f"/runs/{run_id}").json() == record
    assert len(client.get("/runs").json()) == 2
    restarted = RunStore(str(tmp_path / "runs.db"))
    assert restarted.get(UUID(run_id)).model_dump(mode="json") == record
    dataset_store.clear()
    assert client.get(f"/runs/{run_id}").json()["dataset"]["name"] == "fixture"


def test_run_input_errors(client, monkeypatch):
    assert client.post("/runs", json={"dataset_id": str(uuid4())}).status_code == 404
    empty = client.post("/datasets", json={"name": "empty"}).json()
    assert client.post("/runs", json={"dataset_id": empty["id"]}).status_code == 422
    assert client.get(f"/runs/{uuid4()}").status_code == 404
    dataset = client.post("/datasets", json={"name": "one", "cases": [{"input": "x", "expected_output": "x"}]}).json()
    assert client.post("/runs", json={"dataset_id": dataset["id"], "prompt_template": "missing placeholder"}).status_code == 422
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert client.post("/runs", json={"dataset_id": dataset["id"], "provider": "anthropic"}).status_code == 503
    assert client.get("/runs?limit=101").status_code == 422
    many = client.post("/datasets", json={"name": "large", "cases": [{"input": "x", "expected_output": "x"}] * 21}).json()
    assert client.post("/runs", json={"dataset_id": many["id"]}).status_code == 422


def test_runner_preserves_provider_failure_and_continues():
    class FlakyProvider(EchoProvider):
        def generate(self, prompt):
            if prompt == "bad": raise ProviderError("Provider timed out")
            return super().generate(prompt)
    dataset = Dataset(name="mixed", cases=[EvaluationCase(input=x, expected_output=x) for x in ["bad", "good"]])
    record = execute_run(dataset, PromptVersion(name="identity", template="{input}"), FlakyProvider())
    assert record.run.status == "failed"
    assert (record.passed_cases, record.failed_cases, record.error_cases) == (1, 0, 1)
    assert record.pass_rate == .5
    assert record.results[0].passed is None
    assert record.results[0].error == "Provider timed out"


def test_anthropic_adapter_parses_text_and_usage():
    def handler(request):
        assert request.headers["x-api-key"] == "test-key"
        return httpx.Response(200, json={"content": [{"type": "text", "text": " 42 "}], "usage": {"input_tokens": 10, "output_tokens": 1}})
    result = AnthropicProvider("test-key", "test-model", httpx.MockTransport(handler)).generate("question")
    assert (result.text, result.input_tokens, result.output_tokens) == ("42", 10, 1)


@pytest.mark.parametrize("mode", ["timeout", "http", "empty", "malformed"])
def test_anthropic_errors_are_safe(mode):
    def handler(request):
        if mode == "timeout": raise httpx.ReadTimeout("secret", request=request)
        if mode == "http": return httpx.Response(429, text="secret provider body")
        if mode == "empty": return httpx.Response(200, json={"content": []})
        return httpx.Response(200, text="not json")
    with pytest.raises(ProviderError) as raised:
        AnthropicProvider("secret", "test-model", httpx.MockTransport(handler)).generate("question")
    assert "secret" not in str(raised.value)
