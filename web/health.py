"""Health check and Sentry initialization for Vrixo.

Features:
    #76 Sentry error tracking setup
    #77 Health check endpoint
"""

from __future__ import annotations

import os
import time

START_TIME = time.time()
VERSION = "0.1.0"


def init_sentry() -> bool:
    """#76: Initialize Sentry if DSN is configured. Returns True if initialized."""
    dsn = os.environ.get("SENTRY_DSN")
    if not dsn:
        return False
    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=float(os.environ.get("SENTRY_TRACES_RATE", "0.1")),
            profiles_sample_rate=float(os.environ.get("SENTRY_PROFILES_RATE", "0.1")),
            environment=os.environ.get("APP_ENV", "development"),
            release=f"vrixo@{VERSION}",
        )
        return True
    except ImportError:
        return False


def health_check() -> dict:
    """#77: Return a health check payload."""
    return {
        "status": "ok",
        "version": VERSION,
        "uptime_s": int(time.time() - START_TIME),
        "environment": os.environ.get("APP_ENV", "development"),
    }


def is_healthy() -> bool:
    """Return True if the app is in a healthy state."""
    try:
        # Basic sanity: we can import torch and at least one AI module
        import torch  # noqa: F401

        from ai.models import background_removal  # noqa: F401

        return True
    except Exception:
        return False
