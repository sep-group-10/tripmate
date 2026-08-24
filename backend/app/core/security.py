import hashlib
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable is not set")

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

ACCESS_TOKEN_COOKIE_NAME = "access_token"
# Secure cookies are only sent over HTTPS. Local dev runs on plain HTTP,
# so the Secure flag is only forced on outside of development.
COOKIE_SECURE = os.getenv("ENVIRONMENT", "development") != "development"


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt (random salt per call)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    """Create a signed, short-lived JWT access token for a user."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        # Guarantees a distinct token even if issued in the same second
        # as a previous one, since JWT timestamps have only second
        # precision.
        "jti": secrets.token_urlsafe(16),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: uuid.UUID) -> tuple[str, datetime]:
    """Create a signed, long-lived JWT refresh token for a user.
    Returns (token, expires_at) - the caller is responsible for storing
    a hash of the token (see hash_refresh_token) alongside expires_at."""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        # Guarantees a distinct token even if issued in the same second
        # as a previous one, since JWT timestamps have only second
        # precision and would otherwise collide on rapid rotation.
        "jti": secrets.token_urlsafe(16),
        "iat": now,
        "exp": expires_at,
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token, expires_at


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token before storing it in the database, so a
    database leak alone can't be used to authenticate as a user - only
    the token value itself (never persisted) can."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
