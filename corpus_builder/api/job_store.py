"""In-memory job store for tracking background ingestion jobs.

Keeps a dict of job_id → JobState in process memory.
Fine for a local tool — no persistence across restarts is needed.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from corpus_builder.api.schemas import JobStatus, QueryProgress


class JobState:
    def __init__(self, queries: list[str]):
        self.job_id: str = str(uuid.uuid4())
        self.status: JobStatus = JobStatus.PENDING
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        self.query_progress: dict[str, QueryProgress] = {
            q: QueryProgress(query=q) for q in queries
        }

    @property
    def total_papers_processed(self) -> int:
        return sum(qp.papers_processed for qp in self.query_progress.values())

    @property
    def total_chunks_indexed(self) -> int:
        return sum(qp.chunks_indexed for qp in self.query_progress.values())


# Module-level job registry
_jobs: dict[str, JobState] = {}


def create_job(queries: list[str]) -> JobState:
    job = JobState(queries)
    _jobs[job.job_id] = job
    return job


def get_job(job_id: str) -> Optional[JobState]:
    return _jobs.get(job_id)


def list_jobs() -> list[JobState]:
    return list(_jobs.values())
