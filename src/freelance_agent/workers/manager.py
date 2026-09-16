from freelance_agent.core.models import WorkRequest, WorkerResult

from .base import Worker
from .kaggle import KaggleWorker
from .local import LocalWorker


class WorkerManager:
    def __init__(self, workers: list[Worker] | None = None) -> None:
        self.workers = workers or [KaggleWorker(), LocalWorker()]

    def select(self, request: WorkRequest) -> Worker:
        if request.requires_gpu:
            for worker in self.workers:
                if worker.provider == "kaggle" and worker.available():
                    return worker
            raise RuntimeError("No GPU worker currently available")
        for worker in self.workers:
            if worker.available():
                return worker
        raise RuntimeError("No worker currently available")

    def execute(self, request: WorkRequest) -> WorkerResult:
        return self.select(request).execute(request)
