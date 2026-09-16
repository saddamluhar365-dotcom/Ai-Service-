from fastapi.testclient import TestClient

from freelance_agent.app import app
from freelance_agent.workers.kaggle import KaggleWorker


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_job_requires_api_key() -> None:
    client = TestClient(app)
    response = client.post("/jobs", params={"task": "profile data"})
    assert response.status_code == 401


def test_kaggle_is_unavailable_without_credentials(monkeypatch) -> None:
    monkeypatch.delenv("KAGGLE_USERNAME", raising=False)
    monkeypatch.delenv("KAGGLE_API_TOKEN", raising=False)
    worker = KaggleWorker()
    assert worker.available() is False
