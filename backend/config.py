"""Runtime configuration, read from environment variables (prefix ``VRIXO_``)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_JWT_SECRET = "dev-only-secret-change-me-before-deploying-vrixo"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VRIXO_", env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./vrixo_api.db"
    redis_url: str = "redis://localhost:6379/0"
    storage_dir: Path = Path("./storage")

    env: str = "development"  # "production" refuses to start with the default secret
    jwt_secret: str = DEFAULT_JWT_SECRET
    jwt_ttl_minutes: int = 60 * 24

    max_upload_mb: int = 10
    max_image_pixels: int = 40_000_000  # ~40 MP; rejects decompression bombs

    daily_job_limit: int = 50  # jobs a user may submit per UTC day
    max_active_jobs_per_user: int = 3  # queued + running, per user
    max_queue_depth: int = 100  # queued jobs across all users before the API sheds load

    job_soft_time_limit_s: int = 300
    celery_always_eager: bool = False  # run tasks inline (tests, no Redis needed)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
