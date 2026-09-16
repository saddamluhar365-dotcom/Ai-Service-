from datetime import datetime, timezone
from threading import RLock

from .models import Checkpoint, JobRecord, JobState


class InMemoryState:
    """Deterministic development store; production storage will be PostgreSQL-backed."""

    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._checkpoints: dict[str, Checkpoint] = {}
        self._lock = RLock()

    def create(self, job: JobRecord) -> JobRecord:
        with self._lock:
            if job.job_id in self._jobs:
                return self._jobs[job.job_id]
            self._jobs[job.job_id] = job
            return job

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._jobs.get(job_id)

    def transition(self, job_id: str, state: JobState, error: str | None = None) -> JobRecord:
        with self._lock:
            job = self._jobs[job_id]
            job.state = state
            job.last_error = error
            job.updated_at = datetime.now(timezone.utc)
            return job

    def checkpoint(self, checkpoint: Checkpoint) -> None:
        with self._lock:
            self._checkpoints[checkpoint.job_id] = checkpoint
            job = self._jobs[checkpoint.job_id]
            job.checkpoint = checkpoint.stage
            job.state = JobState.CHECKPOINTED
            job.updated_at = checkpoint.created_at

    def latest_checkpoint(self, job_id: str) -> Checkpoint | None:
        with self._lock:
            return self._checkpoints.get(job_id)
