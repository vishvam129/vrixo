"""Friendly error handling for Vrixo.

Features:
    #62 Friendly error messages for failed uploads
    #63 Retry mechanism for transient AI pipeline failures
    #64 Graceful handling when an AI model file is missing
    #65 404 and 500 error helpers
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import TypeVar

logger = logging.getLogger("vrixo")

T = TypeVar("T")


class VrixoError(Exception):
    """Base class for friendly Vrixo errors."""

    user_message: str = "Something went wrong. Please try again."


class UploadFailedError(VrixoError):
    user_message = "Image could not be read. Please try a different photo."


class ModelNotLoadedError(VrixoError):
    user_message = "AI model not loaded. Please contact support."


class QuotaExceededError(VrixoError):
    user_message = "Daily quota reached. Upgrade to Pro for unlimited access."


class UnsupportedFormatError(VrixoError):
    user_message = "This file format is not supported. Use JPG, PNG, or WebP."


def friendly_error_message(exc: Exception) -> str:
    """#62: Map any exception to a user-friendly message."""
    if isinstance(exc, VrixoError):
        return exc.user_message
    if isinstance(exc, FileNotFoundError):
        return "Model or resource not found. Please contact support."
    if isinstance(exc, MemoryError):
        return "Image too large to process. Try a smaller image."
    if isinstance(exc, ValueError):
        return str(exc) if str(exc) else "Invalid input."
    return "Something went wrong. Please try again in a moment."


def retry_on_failure(
    fn: Callable[..., T],
    *args,
    max_attempts: int = 3,
    backoff_seconds: float = 1.0,
    **kwargs,
) -> T:
    """#63: Retry a function on transient failures with exponential backoff.

    Raises the last exception if all attempts fail.
    """
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            last_exc = exc
            logger.warning("Attempt %d/%d failed: %s", attempt, max_attempts, exc)
            if attempt < max_attempts:
                time.sleep(backoff_seconds * (2 ** (attempt - 1)))
    # All retries exhausted
    assert last_exc is not None
    raise last_exc


def handle_missing_model(model_name: str) -> None:
    """#64: Raise a friendly error when a model file is missing."""
    raise ModelNotLoadedError(f"Model '{model_name}' could not be loaded")


def page_not_found_payload() -> dict:
    """#65: Structured payload for a 404 page."""
    return {
        "status": 404,
        "title": "Page not found",
        "message": "The page you're looking for doesn't exist.",
        "action": "Go to home",
        "href": "/",
    }


def internal_error_payload() -> dict:
    """#65: Structured payload for a 500 page."""
    return {
        "status": 500,
        "title": "Something went wrong",
        "message": "Our servers are having a moment. Please try again shortly.",
        "action": "Retry",
        "href": "/",
    }
