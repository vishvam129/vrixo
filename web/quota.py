"""Rate limiting and quota tracking for Vrixo.

Features:
    #55 Track usage per user per day
    #56 Enforce free tier limit (5/day)
    #57 Reset counter at midnight UTC
    #58 Show remaining quota in UI
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from web.auth import _db

FREE_TIER_DAILY_LIMIT = 5
PRO_TIER_DAILY_LIMIT = 1000


def _should_reset(last_reset: str | None) -> bool:
    """Return True if the user's quota should reset (new UTC day)."""
    if last_reset is None:
        return True
    try:
        last = datetime.fromisoformat(last_reset)
        if last.tzinfo is None:
            last = last.replace(tzinfo=UTC)
    except ValueError:
        return True
    now = datetime.now(UTC)
    return (now.date() - last.date()) >= timedelta(days=1)


def _current_reset_timestamp() -> str:
    """Return the ISO timestamp for 'now' in UTC."""
    return datetime.now(UTC).isoformat()


def _get_user_quota(email: str) -> tuple[int, str, str]:
    """Return (daily_usage, tier, daily_reset_at) for a user."""
    conn = _db()
    try:
        row = conn.execute(
            "SELECT daily_usage, tier, daily_reset_at FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        if row is None:
            return 0, "free", _current_reset_timestamp()
        return row[0] or 0, row[1] or "free", row[2] or _current_reset_timestamp()
    finally:
        conn.close()


def _maybe_reset(email: str) -> None:
    """Reset daily usage if it's a new day (#57)."""
    usage, _tier, last_reset = _get_user_quota(email)
    if _should_reset(last_reset):
        conn = _db()
        try:
            conn.execute(
                "UPDATE users SET daily_usage = 0, daily_reset_at = ? WHERE email = ?",
                (_current_reset_timestamp(), email),
            )
            conn.commit()
        finally:
            conn.close()


def get_remaining_quota(email: str) -> int:
    """Return the number of operations the user can still perform today (#58)."""
    if not email:
        return 0
    _maybe_reset(email)
    usage, tier, _ = _get_user_quota(email)
    limit = PRO_TIER_DAILY_LIMIT if tier == "pro" else FREE_TIER_DAILY_LIMIT
    return max(0, limit - usage)


def decrement_quota(email: str) -> bool:
    """Consume one quota credit. Returns True if successful, False if over limit (#55, #56)."""
    if not email:
        return False
    _maybe_reset(email)
    remaining = get_remaining_quota(email)
    if remaining <= 0:
        return False
    conn = _db()
    try:
        conn.execute(
            "UPDATE users SET daily_usage = daily_usage + 1 WHERE email = ?",
            (email,),
        )
        conn.commit()
        return True
    finally:
        conn.close()
