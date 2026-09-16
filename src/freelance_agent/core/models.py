from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class JobState(StrEnum):
    RECEIVED = "received"
    PLANNED = "planned"
    QUEUED = "queued"
    RUNNING = "running"
    CHECKPOINTED = "checkpointed"
    VALIDATING = "validating"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    RECOVERING = "recovering"
    HUMAN_REVIEW = "human_review"


class JobRecord(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid4()))
    state: JobState = JobState.RECEIVED
    payload: dict[str, Any] = Field(default_factory=dict)
    checkpoint: str | None = None
    attempts: int = 0
    provider_attempts: dict[str, int] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    last_error: str | None = None


class Checkpoint(BaseModel):
    job_id: str
    stage: str
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class WorkRequest(BaseModel):
    job_id: str
    task: str
    input_path: str | None = None
    output_path: str | None = None
    requires_gpu: bool = False
    estimated_memory_mb: int = 512


class WorkerResult(BaseModel):
    job_id: str
    provider: str
    status: str
    output_path: str | None = None
    checkpoint: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
