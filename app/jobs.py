from __future__ import annotations

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
import threading
import time
import uuid


@dataclass
class Job:
    job_id: str
    status: str = "queued"  # queued | running | done | error
    progress: float = 0.0
    error: Optional[str] = None
    result: Any = None
    meta: Dict[str, Any] = field(default_factory=dict)


class JobStore:
    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self) -> Job:
        job = Job(job_id=str(uuid.uuid4()))
        with self._lock:
            self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **kwargs: Any) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            for k, v in kwargs.items():
                setattr(job, k, v)


job_store = JobStore()


