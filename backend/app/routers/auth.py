import uuid
from datetime import datetime, timezone

import jwt
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import ApiError, ErrorCode
from app.core.security import (
    ACCESS_TOKEN_COOKIE_NAME,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    COOKIE_SECURE,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    LoginData,
    LoginRequest,
    LogoutRequest,
    RefreshData,
    RefreshRequest,
)
from app.schemas.common import ApiResponse
from app.schemas.user import UserRegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_access_token_cookie(response: Response, access_token: str) -> None:
    """Set the access token as an httpOnly cookie so it is inaccessible
    to client-side scripts."""
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def _rotate_tokens(user: User, db: Session) -> tuple[str, str]:
    """Issue a new access/refresh token pair and store only the refresh
    token's hash, so a database leak cannot be used to authenticate.
    Overwriting the stored hash invalidates the previous refresh token."""
    access_token = create_access_token(user.id, user.role)
    refresh_token, refresh_token_expiry = create_refresh_token(user.id)

    user.refresh_token = hash_refresh_token(refresh_token)
    user.refresh_token_expiry = refresh_token_expiry
    db.add(user)
    db.commit()
    db.refresh(user)

    return access_token, refresh_token


def _issue_tokens(user: User, response: Response, db: Session) -> LoginData:
    """Issue tokens for a login/register, set the access token cookie,
    and return the full response data including the user."""
    access_token, refresh_token = _rotate_tokens(user, db)
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
    """Register a new user with the default role and log them in
    immediately."""
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
        # Concurrent duplicate registrations are caught by the unique
        # constraint, not the check above.
        db.rollback()
        raise ApiError(
            ErrorCode.EMAIL_ALREADY_EXISTS, "Email is already registered"
        ) from exc
    db.refresh(user)

    return ApiResponse(data=_issue_tokens(user, response, db))


# Used to keep response time constant when the email does not exist.
_DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing-safety")


@router.post("/login", response_model=ApiResponse[LoginData])
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Verify credentials and issue tokens for the session."""
    user = db.query(User).filter(User.email == payload.email).first()
    password_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH
    password_is_valid = verify_password(payload.password, password_hash)

    # Same error for unknown email and wrong password, to avoid
    # revealing which emails are registered.
    if user is None or not password_is_valid:
        raise ApiError(ErrorCode.INVALID_CREDENTIALS, "Invalid email or password")

    if not user.is_active:
        raise ApiError(ErrorCode.ACCOUNT_DEACTIVATED, "Account has been deactivated")

    return ApiResponse(data=_issue_tokens(user, response, db))


@router.post("/refresh", response_model=ApiResponse[RefreshData])
def refresh(payload: RefreshRequest, response: Response, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access/refresh pair.
    The old refresh token is invalidated in the same call."""
    try:
        claims = jwt.decode(
            payload.refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
        )
    except jwt.InvalidTokenError as exc:
        raise ApiError(
            ErrorCode.INVALID_REFRESH_TOKEN, "Refresh token is invalid or expired"
        ) from exc

    if claims.get("type") != "refresh":
        raise ApiError(
            ErrorCode.INVALID_REFRESH_TOKEN, "Refresh token is invalid or expired"
        )

    try:
        user_id = uuid.UUID(claims.get("sub", ""))
    except ValueError as exc:
        raise ApiError(
            ErrorCode.INVALID_REFRESH_TOKEN, "Refresh token is invalid or expired"
        ) from exc

    user = db.query(User).filter(User.id == user_id).first()

    # The stored hash must match and not be past its own expiry, so a
    # token that was already rotated out (or never issued) is rejected
    # even though its signature and JWT expiry are still valid.
    token_hash = hash_refresh_token(payload.refresh_token)
    is_valid = (
        user is not None
        and user.refresh_token == token_hash
        and user.refresh_token_expiry is not None
        and user.refresh_token_expiry > datetime.now(timezone.utc)
    )
    if not is_valid:
        raise ApiError(
            ErrorCode.INVALID_REFRESH_TOKEN, "Refresh token is invalid or expired"
        )

    if not user.is_active:
        raise ApiError(ErrorCode.ACCOUNT_DEACTIVATED, "Account has been deactivated")

    access_token, new_refresh_token = _rotate_tokens(user, db)
    _issue_access_token_cookie(response, access_token)

    return ApiResponse(
        data=RefreshData(access_token=access_token, refresh_token=new_refresh_token)
    )


@router.post("/logout", response_model=ApiResponse[dict])
def logout(
    response: Response,
    payload: LogoutRequest | None = None,
    db: Session = Depends(get_db),
):
    """Clear the access token cookie and revoke the refresh token, so
    neither can be used again after logout."""
    if payload is not None and payload.refresh_token is not None:
        token_hash = hash_refresh_token(payload.refresh_token)
        user = db.query(User).filter(User.refresh_token == token_hash).first()
        if user is not None:
            user.refresh_token = None
            user.refresh_token_expiry = None
            db.add(user)
            db.commit()

    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
    )
    return ApiResponse(data={})
