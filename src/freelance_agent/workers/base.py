from abc import ABC, abstractmethod

from freelance_agent.core.models import WorkRequest, WorkerResult


class Worker(ABC):
    provider: str

    @abstractmethod
    def execute(self, request: WorkRequest) -> WorkerResult:
        raise NotImplementedError

    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError
