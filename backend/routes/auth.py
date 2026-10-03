"""Sign-up, log-in and the current user."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.deps import CurrentUser, DbSession
from backend.models import User
from backend.schemas import Credentials, Token, UserOut
from backend.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(body: Credentials, db: DbSession) -> Token:
    password_hash, salt = hash_password(body.password)
    user = User(email=body.email.lower(), password_hash=password_hash, password_salt=salt)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # the unique index on email is the source of truth
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered") from None
    return Token(access_token=create_access_token(user.id))


@router.post("/login", response_model=Token)
def login(body: Credentials, db: DbSession) -> Token:
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    # same error whether the email or the password is wrong
    if user is None or not verify_password(body.password, user.password_hash, user.password_salt):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser) -> User:
    return user
