from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import Field, field_validator
from app.schemas.domain import DomainModel, Dataset, EvaluationRun, EvaluationResult, PromptVersion


class RunRequest(DomainModel):
    dataset_id: UUID
    provider: Literal["echo", "anthropic"] = "echo"
    prompt_name: str = Field(default="identity", min_length=1, max_length=100)
    prompt_version: int = Field(default=1, ge=1)
    prompt_template: str = Field(default="{input}", min_length=1, max_length=4000)

    @field_validator("prompt_template")
    @classmethod
    def require_input_placeholder(cls, value: str) -> str:
        if "{input}" not in value:
            raise ValueError("Prompt template must contain {input}")
        return value


class RunRecord(DomainModel):
    run: EvaluationRun
    dataset: Dataset
    prompt: PromptVersion
    results: list[EvaluationResult]
    completed_at: datetime
    passed_cases: int
    failed_cases: int
    error_cases: int
    pass_rate: float = Field(ge=0, le=1)
    mean_latency_ms: float = Field(ge=0)
