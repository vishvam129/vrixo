"""Tests for web.errors."""

import pytest

from web.errors import (
    ModelNotLoadedError,
    UnsupportedFormatError,
    UploadFailedError,
    friendly_error_message,
    handle_missing_model,
    internal_error_payload,
    page_not_found_payload,
    retry_on_failure,
)


def test_friendly_error_upload_failed() -> None:
    """#62: upload errors produce friendly messages."""
    msg = friendly_error_message(UploadFailedError())
    assert "Image could not be read" in msg


def test_friendly_error_model_not_loaded() -> None:
    msg = friendly_error_message(ModelNotLoadedError())
    assert "contact support" in msg


def test_friendly_error_memory_error() -> None:
    msg = friendly_error_message(MemoryError())
    assert "too large" in msg


def test_friendly_error_unsupported_format() -> None:
    msg = friendly_error_message(UnsupportedFormatError())
    assert "JPG" in msg or "PNG" in msg


def test_friendly_error_generic_exception_has_fallback() -> None:
    msg = friendly_error_message(Exception("raw internals"))
    assert "Something went wrong" in msg
    # Raw exception message should NOT leak through
    assert "raw internals" not in msg


def test_retry_on_failure_succeeds_on_second_attempt() -> None:
    """#63: retry should succeed if a later attempt works."""
    calls = {"count": 0}

    def flaky() -> str:
        calls["count"] += 1
        if calls["count"] < 2:
            raise RuntimeError("transient")
        return "ok"

    result = retry_on_failure(flaky, max_attempts=3, backoff_seconds=0.01)
    assert result == "ok"
    assert calls["count"] == 2


def test_retry_on_failure_raises_after_exhaustion() -> None:
    """#63: all retries exhausted re-raises the last exception."""

    def always_fails() -> None:
        raise ValueError("persistent failure")

    with pytest.raises(ValueError, match="persistent failure"):
        retry_on_failure(always_fails, max_attempts=3, backoff_seconds=0.01)


def test_handle_missing_model_raises() -> None:
    """#64: missing model raises a friendly error."""
    with pytest.raises(ModelNotLoadedError):
        handle_missing_model("u2net")


def test_page_not_found_payload_shape() -> None:
    """#65: 404 payload has expected keys."""
    payload = page_not_found_payload()
    assert payload["status"] == 404
    assert "title" in payload
    assert "href" in payload


def test_internal_error_payload_shape() -> None:
    """#65: 500 payload has expected keys."""
    payload = internal_error_payload()
    assert payload["status"] == 500
    assert "title" in payload
    assert "href" in payload
