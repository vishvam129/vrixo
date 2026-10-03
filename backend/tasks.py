"""The worker task that runs one image job."""

from __future__ import annotations

import tempfile
import time
from pathlib import Path

from celery.exceptions import SoftTimeLimitExceeded
from sqlalchemy import update

from backend.db import get_sessionmaker
from backend.models import Job, JobStatus, utcnow
from backend.pipelines import run_operation
from backend.queue import celery_app
from backend.storage import get_storage


@celery_app.task(name="vrixo.process_job")
def process_job(job_id: str) -> str:
    """Run a queued job and record the outcome. Returns the final status.

    Safe to deliver more than once: the queued → running transition is a single
    conditional UPDATE, so if a second worker receives the same job (redelivery
    after a crash, or a duplicate message) it finds nothing to claim and exits.
    """
    session_factory = get_sessionmaker()
    storage = get_storage()

    with session_factory() as session:
        claimed = session.execute(
            update(Job)
            .where(Job.id == job_id, Job.status == JobStatus.QUEUED)
            .values(status=JobStatus.RUNNING, started_at=utcnow())
        )
        session.commit()
        if claimed.rowcount == 0:
            job = session.get(Job, job_id)
            return job.status.value if job else "missing"

        job = session.get(Job, job_id)
        assert job is not None
        operation, params = job.operation, dict(job.params)
        source_key = job.upload.storage_key
        result_key = f"results/{job.user_id}/{job.id}.png"

    started = time.perf_counter()
    status, error = JobStatus.SUCCEEDED, None
    try:
        with tempfile.TemporaryDirectory(prefix="vrixo-job-") as tmp:
            output = Path(tmp) / "result.png"
            run_operation(operation, params, storage.local_path(source_key), output)
            storage.save(result_key, output.read_bytes())
    except SoftTimeLimitExceeded:
        status, error = JobStatus.FAILED, "job exceeded the time limit"
    except Exception as exc:  # the job is marked failed; the worker keeps running
        status, error = JobStatus.FAILED, f"{type(exc).__name__}: {exc}"[:2000]

    with session_factory() as session:
        session.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(
                status=status,
                error=error,
                result_key=result_key if status is JobStatus.SUCCEEDED else None,
                finished_at=utcnow(),
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
        )
        session.commit()
    return status.value
