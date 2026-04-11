"""Tests for web.quota."""

from pathlib import Path

import pytest

from web import auth, quota
from web.auth import signup
from web.quota import decrement_quota, get_remaining_quota


@pytest.fixture(autouse=True)
def temp_db(tmp_path: Path, monkeypatch) -> None:
    """Use a throwaway SQLite DB for every test."""
    monkeypatch.setattr(auth, "DB_PATH", tmp_path / "test.db")


def test_new_user_has_full_free_quota() -> None:
    signup("alice@example.com", "strongpass123")
    remaining = get_remaining_quota("alice@example.com")
    assert remaining == quota.FREE_TIER_DAILY_LIMIT


def test_decrement_quota_reduces_remaining() -> None:
    signup("bob@example.com", "strongpass123")
    before = get_remaining_quota("bob@example.com")
    success = decrement_quota("bob@example.com")
    assert success is True
    after = get_remaining_quota("bob@example.com")
    assert after == before - 1


def test_decrement_at_zero_returns_false() -> None:
    """Users at quota limit cannot use more operations."""
    signup("carol@example.com", "strongpass123")
    for _ in range(quota.FREE_TIER_DAILY_LIMIT):
        decrement_quota("carol@example.com")
    assert get_remaining_quota("carol@example.com") == 0
    # Next decrement should fail
    assert decrement_quota("carol@example.com") is False


def test_empty_email_has_zero_quota() -> None:
    assert get_remaining_quota("") == 0
    assert decrement_quota("") is False


def test_nonexistent_user_quota() -> None:
    # Creating a user-less quota query should still return something sane
    remaining = get_remaining_quota("ghost@example.com")
    assert remaining >= 0
