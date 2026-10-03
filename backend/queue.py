"""Celery application — the job queue between the API and the worker.

The API only writes a job row and publishes its id; the worker (a separate
process, ``celery -A backend.queue worker``) does the slow image processing.
"""

from __future__ import annotations

from celery import Celery

from backend.config import get_settings

settings = get_settings()

celery_app = Celery("vrixo", broker=settings.redis_url, include=["backend.tasks"])
celery_app.conf.update(
    task_always_eager=settings.celery_always_eager,
    task_ignore_result=True,  # job state lives in PostgreSQL, not in the result backend
    # image jobs are long and memory-heavy: take one at a time, and only
    # acknowledge after finishing so a crashed worker's job is redelivered
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_soft_time_limit=settings.job_soft_time_limit_s,
    task_time_limit=settings.job_soft_time_limit_s + 30,
    broker_connection_retry_on_startup=True,
)


def enqueue(job_id: str) -> None:
    """Publish a job for the worker."""
    from backend.tasks import process_job

    process_job.delay(job_id)
