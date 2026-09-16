from .models import Checkpoint, JobRecord, JobState, WorkRequest, WorkerResult
from .state import InMemoryState
from freelance_agent.workers.manager import WorkerManager


class Orchestrator:
    def __init__(
        self, state: InMemoryState | None = None, workers: WorkerManager | None = None
    ) -> None:
        self.state = state or InMemoryState()
        self.workers = workers or WorkerManager()

    def submit(self, task: str, payload: dict[str, object] | None = None) -> JobRecord:
        job = JobRecord(payload=payload or {})
        self.state.create(job)
        self.state.transition(job.job_id, JobState.PLANNED)
        return job

    def run(self, job_id: str, request: WorkRequest) -> WorkerResult:
        job = self.state.get(job_id)
        if job is None:
            raise KeyError(job_id)
        self.state.transition(job_id, JobState.QUEUED)
        try:
            self.state.transition(job_id, JobState.RUNNING)
            result = self.workers.execute(request)
            self.state.checkpoint(
                Checkpoint(
                    job_id=job_id,
                    stage=result.checkpoint or result.status,
                    data=result.metadata,
                )
            )
            return result
        except Exception as exc:
            self.state.transition(job_id, JobState.RECOVERING, error=str(exc))
            raise
