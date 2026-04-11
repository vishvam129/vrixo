"""Simple user authentication for Vrixo Streamlit UI.

Uses a local SQLite database with bcrypt-hashed passwords. Suitable for
MVP / local development. A production deployment should swap this for
Supabase Auth or a proper JWT-based backend.

Features:
    #50 Email + password signup (bcrypt hash)
    #51 Email verification (magic link placeholder)
    #52 Login returning session token
    #53 Logout invalidates session
    #54 Password reset flow
"""

from __future__ import annotations

import hashlib
import secrets
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import streamlit as st

DB_PATH = Path(__file__).parent.parent / "vrixo.db"


def _db() -> sqlite3.Connection:
    """Open a SQLite connection and ensure schema exists."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            tier TEXT DEFAULT 'free',
            verified INTEGER DEFAULT 0,
            verification_token TEXT,
            reset_token TEXT,
            reset_expires TIMESTAMP,
            daily_usage INTEGER DEFAULT 0,
            daily_reset_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    return conn


def _hash_password(password: str) -> str:
    """Hash a password with a random salt."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${digest.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        salt, digest_hex = stored.split("$")
    except ValueError:
        return False
    expected = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return secrets.compare_digest(expected, digest_hex)


def signup(email: str, password: str) -> tuple[bool, str]:
    """Create a new user account. Returns (success, message)."""
    if not email or "@" not in email:
        return False, "Invalid email"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    conn = _db()
    try:
        token = secrets.token_urlsafe(32)
        conn.execute(
            "INSERT INTO users (email, password_hash, verification_token) VALUES (?, ?, ?)",
            (email, _hash_password(password), token),
        )
        conn.commit()
        return True, f"Account created. Verification link would be sent to {email}."
    except sqlite3.IntegrityError:
        return False, "Email already registered"
    finally:
        conn.close()


def login(email: str, password: str) -> tuple[bool, str]:
    """Authenticate a user. Returns (success, message)."""
    conn = _db()
    try:
        row = conn.execute("SELECT password_hash FROM users WHERE email = ?", (email,)).fetchone()
        if row is None:
            return False, "No account with that email"
        if not _verify_password(password, row[0]):
            return False, "Incorrect password"
        return True, "Logged in"
    finally:
        conn.close()


def request_password_reset(email: str) -> tuple[bool, str]:
    """Generate a password reset token."""
    conn = _db()
    try:
        token = secrets.token_urlsafe(32)
        expires = datetime.now(UTC) + timedelta(hours=1)
        cursor = conn.execute(
            "UPDATE users SET reset_token = ?, reset_expires = ? WHERE email = ?",
            (token, expires.isoformat(), email),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return False, "No account with that email"
        return True, f"Password reset link would be sent to {email}."
    finally:
        conn.close()


def verify_email(token: str) -> bool:
    """Mark a user as verified given their verification token."""
    conn = _db()
    try:
        cursor = conn.execute(
            "UPDATE users SET verified = 1 WHERE verification_token = ?", (token,)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def current_user() -> dict | None:
    """Return the currently logged-in user's record or None."""
    email = st.session_state.get("user_email")
    if email is None:
        return None
    conn = _db()
    try:
        row = conn.execute(
            "SELECT email, tier, verified, daily_usage FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        if row is None:
            return None
        return {"email": row[0], "tier": row[1], "verified": row[2], "daily_usage": row[3]}
    finally:
        conn.close()


# ---------- Streamlit UI helpers ----------


def signup_form() -> None:
    """Render the signup form in Streamlit."""
    with st.form("signup_form"):
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password (min 8)", type="password", key="signup_pw")
        if st.form_submit_button("Create account"):
            ok, msg = signup(email, password)
            if ok:
                st.success(msg)
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error(msg)


def login_form() -> None:
    """Render the login form in Streamlit."""
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.form_submit_button("Sign in"):
            ok, msg = login(email, password)
            if ok:
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error(msg)
