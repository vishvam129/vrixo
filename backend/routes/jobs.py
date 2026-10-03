"""Submit jobs, poll their status, download results."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import ValidationError
from sqlalchemy import func, select

from backend import queue
from backend.config import get_settings
from backend.deps import CurrentUser, DbSession
from backend.models import ACTIVE_STATUSES, Job, JobStatus, Upload
from backend.pipelines import OPERATIONS, validate_params
from backend.schemas import JobCreate, JobOut
from backend.storage import get_storage

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _count(db: DbSession, *conditions: object) -> int:
    return db.scalar(select(func.count()).select_from(Job).where(*conditions)) or 0


@router.post("", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
def create_job(body: JobCreate, user: CurrentUser, db: DbSession) -> Job:
    settings = get_settings()

    if body.operation not in OPERATIONS:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"Unknown operation; choose one of: {', '.join(sorted(OPERATIONS))}",
        )
    try:
        params = validate_params(body.operation, body.params)
    except ValidationError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            exc.errors(include_url=False, include_input=False),
        ) from None

    upload = db.get(Upload, body.upload_id)
    if upload is None or upload.user_id != user.id:  # other users' uploads look like "not found"
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Upload not found")

    # --- admission control: protect the worker before accepting more work ---
    midnight = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    if _count(db, Job.user_id == user.id, Job.queued_at >= midnight) >= settings.daily_job_limit:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Daily job limit reached")

    if (
        _count(db, Job.user_id == user.id, Job.status.in_(ACTIVE_STATUSES))
        >= settings.max_active_jobs_per_user
    ):
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Too many jobs in progress; wait for one to finish",
            headers={"Retry-After": "10"},
        )

    if _count(db, Job.status == JobStatus.QUEUED) >= settings.max_queue_depth:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "The queue is full; try again shortly",
            headers={"Retry-After": "30"},
        )

    job = Job(user_id=user.id, upload_id=upload.id, operation=body.operation, params=params)
    db.add(job)
    db.commit()  # the row must exist before the worker can pick the job up

    try:
        queue.enqueue(job.id)
    except Exception as exc:  # broker unreachable: don't leave a job stuck in "queued"
        job.status, job.error = JobStatus.FAILED, f"could not enqueue: {type(exc).__name__}"
        db.commit()
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Queue unavailable") from None

    db.refresh(job)  # in eager mode the task has already run
    return job


def _own_job(db: DbSession, user_id: str, job_id: str) -> Job:
    job = db.get(Job, job_id)
    if job is None or job.user_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return job


@router.get("", response_model=list[JobOut])
def list_jobs(user: CurrentUser, db: DbSession, limit: int = 20) -> list[Job]:
    query = (
        select(Job)
        .where(Job.user_id == user.id)
        .order_by(Job.queued_at.desc())
        .limit(max(1, min(limit, 100)))
    )
    return list(db.scalars(query))


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: str, user: CurrentUser, db: DbSession) -> Job:
    return _own_job(db, user.id, job_id)


@router.get("/{job_id}/result")
def get_result(job_id: str, user: CurrentUser, db: DbSession) -> FileResponse:
    job = _own_job(db, user.id, job_id)
    if job.status is not JobStatus.SUCCEEDED or job.result_key is None:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Job is {job.status.value}; no result yet")
    return FileResponse(
        get_storage().local_path(job.result_key),
        media_type="image/png",
        filename=f"vrixo-{job.operation}-{job.id[:8]}.png",
    )
