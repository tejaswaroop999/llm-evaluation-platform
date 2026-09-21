from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvaluationCase(DomainModel):
    id: UUID = Field(default_factory=uuid4)
    input: str = Field(min_length=1)
    expected_output: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Dataset(DomainModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1)
    description: str | None = None
    cases: list[EvaluationCase] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PromptVersion(DomainModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1)
    version: int = Field(default=1, ge=1)
    template: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvaluationRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvaluationRun(DomainModel):
    id: UUID = Field(default_factory=uuid4)
    dataset_id: UUID
    prompt_version_id: UUID
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    evaluator_names: list[str] = Field(default_factory=list)
    status: EvaluationRunStatus = EvaluationRunStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvaluationResult(DomainModel):
    id: UUID = Field(default_factory=uuid4)
    run_id: UUID
    case_id: UUID
    input: str
    expected_output: str
    actual_output: str | None = None
    passed: bool | None = None
    score: float | None = Field(default=None, ge=0, le=1)
    latency_ms: float | None = Field(default=None, ge=0)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    estimated_cost: float | None = Field(default=None, ge=0)
    error: str | None = None