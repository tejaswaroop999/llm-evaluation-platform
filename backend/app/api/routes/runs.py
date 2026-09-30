import os
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from app.db.runs import RunStore
from app.schemas import PromptVersion
from app.schemas.runs import RunRequest, RunRecord
from app.services.datasets import dataset_store
from app.services.providers.adapters import EchoProvider, AnthropicProvider
from app.services.runner import execute_run

router = APIRouter(prefix="/runs", tags=["runs"])


def get_run_store() -> RunStore:
    return RunStore(os.environ.get("EVALUATION_DB_PATH", "data/evaluations.db"))


@router.post("", response_model=RunRecord, status_code=201)
def create_run(request: RunRequest, store: RunStore = Depends(get_run_store)) -> RunRecord:
    dataset = dataset_store.get(request.dataset_id)
    if dataset is None:
        raise HTTPException(404, "Dataset not found")
    if not dataset.cases:
        raise HTTPException(422, "Dataset must have at least one case")
    if len(dataset.cases) > 20 or any(len(case.input) > 4000 for case in dataset.cases):
        raise HTTPException(422, "Runs support at most 20 cases with inputs up to 4000 characters")
    if any(len(request.prompt_template.replace("{input}", case.input)) > 12000 for case in dataset.cases):
        raise HTTPException(422, "Rendered prompts must be at most 12000 characters")
    provider = EchoProvider()
    if request.provider == "anthropic":
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise HTTPException(503, "ANTHROPIC_API_KEY is not configured")
        provider = AnthropicProvider(key, os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6"))
    prompt = PromptVersion(name=request.prompt_name, version=request.prompt_version,
                           template=request.prompt_template)
    record = execute_run(dataset, prompt, provider)
    store.save(record)
    return record


@router.get("", response_model=list[RunRecord])
def list_runs(limit: int = Query(default=100, ge=1, le=100),
              store: RunStore = Depends(get_run_store)) -> list[RunRecord]:
    return store.list(limit)


@router.get("/{run_id}", response_model=RunRecord)
def get_run(run_id: UUID, store: RunStore = Depends(get_run_store)) -> RunRecord:
    record = store.get(run_id)
    if record is None:
        raise HTTPException(404, "Run not found")
    return record
