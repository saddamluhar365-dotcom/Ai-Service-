from fastapi import APIRouter, Header, HTTPException

from freelance_agent.core.models import WorkRequest
from freelance_agent.core.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/jobs")
def create_job(task: str, x_api_key: str = Header(default="")) -> dict[str, object]:
    if x_api_key != "change-me":
        raise HTTPException(status_code=401, detail="invalid api key")
    job = orchestrator.submit(task)
    return job.model_dump(mode="json")


@router.post("/jobs/{job_id}/run")
def run_job(
    job_id: str, request: WorkRequest, x_api_key: str = Header(default="")
) -> dict[str, object]:
    if x_api_key != "change-me":
        raise HTTPException(status_code=401, detail="invalid api key")
    if request.job_id != job_id:
        raise HTTPException(status_code=400, detail="job_id mismatch")
    result = orchestrator.run(job_id, request)
    return result.model_dump(mode="json")
