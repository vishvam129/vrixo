"""Tests for web.health."""

from web.health import VERSION, health_check, init_sentry, is_healthy


def test_health_check_returns_ok_payload() -> None:
    """#77: health check returns expected payload shape."""
    payload = health_check()
    assert payload["status"] == "ok"
    assert payload["version"] == VERSION
    assert "uptime_s" in payload
    assert payload["uptime_s"] >= 0


def test_health_check_has_environment() -> None:
    payload = health_check()
    assert "environment" in payload


def test_is_healthy_when_deps_available() -> None:
    """App should be healthy when torch and AI modules import."""
    assert is_healthy() is True


def test_init_sentry_without_dsn_returns_false(monkeypatch) -> None:
    """#76: init_sentry returns False when no DSN is set."""
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    assert init_sentry() is False
