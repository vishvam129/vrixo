"""FastAPI application.

uvicorn backend.main:app --reload
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.config import DEFAULT_JWT_SECRET, get_settings
from backend.db import Base, get_engine
from backend.routes import auth, jobs, uploads


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    if settings.env == "production" and settings.jwt_secret == DEFAULT_JWT_SECRET:
        raise RuntimeError("Set VRIXO_JWT_SECRET before running in production")
    if settings.env != "production":
        # development and tests: create tables directly. Production uses Alembic.
        Base.metadata.create_all(get_engine())
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Vrixo API",
        version="0.2.0",
        description="Upload a photo, submit an image job, poll it, download the result.",
        lifespan=lifespan,
    )
    origins = [
        origin.strip() for origin in get_settings().cors_origins.split(",") if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
        expose_headers=["Retry-After"],
    )
    app.include_router(auth.router)
    app.include_router(uploads.router)
    app.include_router(jobs.router)

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        """Liveness plus a database round-trip."""
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok"}

    return app


app = create_app()
