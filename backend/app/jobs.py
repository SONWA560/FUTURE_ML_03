"""Loads the curated job description library."""

import json
from functools import lru_cache

from app.config import settings
from app.schemas import JobDescription, JobRoleSummary


@lru_cache(maxsize=1)
def _load_all() -> list[JobDescription]:
    raw = json.loads(settings.curated_jobs_path.read_text())
    return [JobDescription(**entry) for entry in raw]


def list_job_roles() -> list[JobRoleSummary]:
    return [
        JobRoleSummary(id=job.id, title=job.title, category=job.category or "")
        for job in _load_all()
    ]


def get_job_role(job_id: str) -> JobDescription | None:
    for job in _load_all():
        if job.id == job_id:
            return job
    return None
