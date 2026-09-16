from freelance_agent.core.models import WorkRequest, WorkerResult

from .base import Worker


class LocalWorker(Worker):
    provider = "local"

    def available(self) -> bool:
        return True

    def execute(self, request: WorkRequest) -> WorkerResult:
        return WorkerResult(
            job_id=request.job_id,
            provider=self.provider,
            status="completed",
            output_path=request.output_path,
            checkpoint="local_complete",
            metadata={"mode": "local"},
        )
