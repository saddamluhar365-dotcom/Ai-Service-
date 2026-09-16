from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from freelance_agent.core.models import WorkRequest, WorkerResult

from .base import Worker


class KaggleWorker(Worker):
    """Short-lived Kaggle Notebook worker using the official Kaggle CLI."""

    provider = "kaggle"

    def __init__(self, username: str | None = None, api_token: str | None = None) -> None:
        self.username = username or os.getenv("KAGGLE_USERNAME")
        self.api_token = api_token or os.getenv("KAGGLE_API_TOKEN")

    def available(self) -> bool:
        if not self.username or not self.api_token:
            return False
        try:
            result = subprocess.run(
                ["kaggle", "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        return result.returncode == 0

    def execute(self, request: WorkRequest) -> WorkerResult:
        if not self.available():
            raise RuntimeError("Kaggle worker is not configured or CLI is unavailable")

        slug = f"freelance-agent-{request.job_id.replace('-', '')[:20]}"
        with tempfile.TemporaryDirectory(prefix="freelance-agent-kaggle-") as temp_dir:
            workdir = Path(temp_dir)
            script = workdir / "worker.py"
            metadata = workdir / "kernel-metadata.json"
            payload = {
                "job_id": request.job_id,
                "task": request.task,
                "input_path": request.input_path,
                "output_path": request.output_path,
                "checkpoint": "kaggle_started",
            }
            script.write_text(
                "import json\n"
                "from pathlib import Path\n"
                f"payload = {json.dumps(payload)!r}\n"
                "Path('worker-result.json').write_text(payload)\n",
                encoding="utf-8",
            )
            metadata.write_text(
                json.dumps(
                    {
                        "id": f"{self.username}/{slug}",
                        "title": slug,
                        "code_file": "worker.py",
                        "language": "python",
                        "kernel_type": "script",
                        "is_private": "true",
                        "enable_gpu": "true" if request.requires_gpu else "false",
                        "enable_internet": "false",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            self._run(["kaggle", "kernels", "push", "-p", str(workdir), "--timeout", "600"])
            return WorkerResult(
                job_id=request.job_id,
                provider=self.provider,
                status="submitted",
                checkpoint="kaggle_submitted",
                metadata={"kernel": f"{self.username}/{slug}"},
            )

    @staticmethod
    def _run(command: list[str]) -> str:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=90,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()[-2000:]
            raise RuntimeError(f"Kaggle command failed: {detail}")
        return result.stdout
