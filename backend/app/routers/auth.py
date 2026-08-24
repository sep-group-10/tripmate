from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import ApiError, ErrorCode
from app.core.security import (
    ACCESS_TOKEN_COOKIE_NAME,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    COOKIE_SECURE,
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginData, LoginRequest
from app.schemas.common import ApiResponse
from app.schemas.user import UserRegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_access_token_cookie(response: Response, access_token: str) -> None:
    """Set the access token as an httpOnly cookie for web clients.
    Shared by register and login so both issue the same cookie."""
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def _issue_tokens(user: User, response: Response, db: Session) -> LoginData:
    """Create an access token + refresh token pair for a user, persist
    the refresh token (hashed) on the user row, set the access token
    cookie, and return the data for the response body. Shared by
    register and login since both log the user in the same way."""
    access_token = create_access_token(user.id, user.role)
    refresh_token, refresh_token_expiry = create_refresh_token(user.id)

    user.refresh_token = hash_refresh_token(refresh_token)
    user.refresh_token_expiry = refresh_token_expiry
    db.add(user)
    db.commit()
    db.refresh(user)

    _issue_access_token_cookie(response, access_token)

    return LoginData(access_token=access_token, refresh_token=refresh_token, user=user)


@router.post(
    "/register",
    response_model=ApiResponse[LoginData],
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserRegisterRequest, response: Response, db: Session = Depends(get_db)
):
    """Register a new user with a hashed password and the default
    TOURIST role, then log them in immediately (same token issuance as
    /login). Rejects the request if the email is already taken."""
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user is not None:
        raise ApiError(ErrorCode.EMAIL_ALREADY_EXISTS, "Email is already registered")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        # Backstop for the race where two requests pass the exists-check
        # above at the same time; the database's unique constraint is
        # the real guard, this just turns the failure into a clean 409.
        db.rollback()
        raise ApiError(
            ErrorCode.EMAIL_ALREADY_EXISTS, "Email is already registered"
        ) from exc
    db.refresh(user)

    return ApiResponse(data=_issue_tokens(user, response, db))


# Hashed once at import time so a login attempt against a nonexistent
# email still runs a real bcrypt comparison, keeping response time
# consistent regardless of whether the email exists.
_DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing-safety")


@router.post("/login", response_model=ApiResponse[LoginData])
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Verify email/password, then issue an access token: set as an
    httpOnly cookie for web clients and also returned in the response
    body for mobile clients."""
    user = db.query(User).filter(User.email == payload.email).first()
    password_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH
    password_is_valid = verify_password(payload.password, password_hash)

    # Same generic error for "no such email" and "wrong password" so a
    # caller can't use this endpoint to find out which emails exist.
    if user is None or not password_is_valid:
        raise ApiError(ErrorCode.INVALID_CREDENTIALS, "Invalid email or password")

    if not user.is_active:
        raise ApiError(ErrorCode.ACCOUNT_DEACTIVATED, "Account has been deactivated")

    return ApiResponse(data=_issue_tokens(user, response, db))


@router.post("/logout", response_model=ApiResponse[dict])
def logout(response: Response):
    """Clear the access token cookie to end the current web session."""
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
    )
    return ApiResponse(data={})
