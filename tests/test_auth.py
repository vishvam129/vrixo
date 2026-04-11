"""Tests for web.auth."""

from pathlib import Path

import pytest

from web import auth
from web.auth import login, request_password_reset, signup, verify_email


@pytest.fixture(autouse=True)
def temp_db(tmp_path: Path, monkeypatch) -> None:
    """Use a throwaway SQLite DB for every test."""
    monkeypatch.setattr(auth, "DB_PATH", tmp_path / "test.db")


def test_signup_creates_account() -> None:
    ok, msg = signup("alice@example.com", "strongpass123")
    assert ok
    assert "alice@example.com" in msg


def test_signup_rejects_short_password() -> None:
    ok, msg = signup("bob@example.com", "short")
    assert not ok
    assert "8 characters" in msg


def test_signup_rejects_invalid_email() -> None:
    ok, _ = signup("not-an-email", "strongpass123")
    assert not ok


def test_signup_rejects_duplicate_email() -> None:
    signup("dup@example.com", "strongpass123")
    ok, msg = signup("dup@example.com", "strongpass123")
    assert not ok
    assert "already" in msg


def test_login_success() -> None:
    signup("carol@example.com", "strongpass123")
    ok, _ = login("carol@example.com", "strongpass123")
    assert ok


def test_login_wrong_password() -> None:
    signup("dave@example.com", "strongpass123")
    ok, msg = login("dave@example.com", "wrong_password")
    assert not ok
    assert "Incorrect" in msg


def test_login_unknown_user() -> None:
    ok, msg = login("ghost@example.com", "whatever")
    assert not ok
    assert "No account" in msg


def test_request_password_reset_known_user() -> None:
    signup("eve@example.com", "strongpass123")
    ok, _ = request_password_reset("eve@example.com")
    assert ok


def test_request_password_reset_unknown_user() -> None:
    ok, _ = request_password_reset("nobody@example.com")
    assert not ok


def test_verify_email_with_valid_token() -> None:
    signup("frank@example.com", "strongpass123")
    # Grab the token from the DB
    import sqlite3

    conn = sqlite3.connect(auth.DB_PATH)
    row = conn.execute(
        "SELECT verification_token FROM users WHERE email = ?",
        ("frank@example.com",),
    ).fetchone()
    conn.close()
    assert row is not None
    token = row[0]

    assert verify_email(token) is True


def test_verify_email_with_invalid_token() -> None:
    assert verify_email("garbage-token") is False
