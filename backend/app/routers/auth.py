import os
import uuid
from datetime import datetime, timezone

import jwt
from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.errors import ApiError, ErrorCode
from app.core.rate_limit import limiter
from app.core.security import (
    ACCESS_TOKEN_COOKIE_NAME,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    COOKIE_SECURE,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    REFRESH_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
    generate_password_reset_token,
    generate_verification_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    ForgotPasswordRequest,
    GoogleLoginRequest,
    LoginData,
    LoginRequest,
    LogoutRequest,
    RefreshData,
    RefreshRequest,
    RegisterData,
    ResendVerificationRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.schemas.common import ApiResponse
from app.schemas.user import UserRegisterRequest
from app.services.email import send_email
from app.services.email_templates import password_reset_email, verification_email

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


def _issue_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    """Set the refresh token as an httpOnly cookie so it is inaccessible
    to client-side scripts."""
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # 7 days in seconds
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
    _issue_refresh_token_cookie(response, refresh_token)
    return LoginData(access_token=access_token, refresh_token=refresh_token, user=user)


def _frontend_base_url() -> str:
    # `or`, not getenv's default arg - an empty-but-set env var must still fall back.
    return os.getenv("FRONTEND_BASE_URL") or "http://localhost:5173"


def _send_verification_email(user: User, db: Session) -> None:
    """Generate a fresh verification token for the user, save it, and
    email the verification link. Shared by register and
    resend-verification."""
    token, expires_at = generate_verification_token()
    user.email_verification_token = token
    user.email_verification_expiry = expires_at
    db.add(user)
    db.commit()

    link = f"{_frontend_base_url()}/verify-email?token={token}"
    subject, body = verification_email(link)
    send_email(user.email, subject, body)


def _send_password_reset_email(user: User, db: Session) -> None:
    """Generate a fresh password-reset token for the user, save it, and
    email the reset link."""
    token, expires_at = generate_password_reset_token()
    user.password_reset_token = token
    user.reset_token_expiry = expires_at
    db.add(user)
    db.commit()

    link = f"{_frontend_base_url()}/reset-password?token={token}"
    subject, body = password_reset_email(link)
    send_email(user.email, subject, body)


@router.post(
    "/register",
    response_model=ApiResponse[RegisterData],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
def register(
    request: Request,
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """Register a new user with the default role. No session is issued
    here - the account can't be used until the email is verified."""
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

    _send_verification_email(user, db)

    return ApiResponse(
        data=RegisterData(
            email=user.email,
            message="Please check your email to verify your account.",
        )
    )


@router.post("/verify-email", response_model=ApiResponse[dict])
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Marks the account verified if the token is valid and unexpired;
    the token is cleared either way, so it can't be replayed."""
    user = db.query(User).filter(User.email_verification_token == payload.token).first()

    is_valid = (
        user is not None
        and user.email_verification_expiry is not None
        and user.email_verification_expiry > datetime.now(timezone.utc)
    )
    if not is_valid:
        raise ApiError(
            ErrorCode.INVALID_VERIFICATION_TOKEN,
            "Verification link is invalid or expired",
        )

    user.is_email_verified = True
    user.email_verification_token = None
    user.email_verification_expiry = None
    db.add(user)
    db.commit()

    return ApiResponse(data={})


@router.post("/resend-verification", response_model=ApiResponse[dict])
@limiter.limit("5/minute")
def resend_verification(
    request: Request,
    payload: ResendVerificationRequest,
    db: Session = Depends(get_db),
):
    """Resends the verification email unless already verified - same
    response either way, so this can't reveal which emails exist."""
    user = db.query(User).filter(User.email == payload.email).first()

    if user is not None and not user.is_email_verified:
        _send_verification_email(user, db)

    return ApiResponse(data={})


# Used to keep response time constant when the email does not exist.
_DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing-safety")


@router.post("/login", response_model=ApiResponse[LoginData])
@limiter.limit("5/minute")
def login(
    request: Request,
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """Verify credentials and issue tokens for the session."""
    user = db.query(User).filter(User.email == payload.email).first()
    # A Google-only account has no password_hash - treat it the same as
    # "wrong password" rather than crashing verify_password on None.
    password_hash = (
        user.password_hash
        if user is not None and user.password_hash is not None
        else _DUMMY_PASSWORD_HASH
    )
    password_is_valid = verify_password(payload.password, password_hash)

    # Same error for unknown email and wrong password, to avoid
    # revealing which emails are registered.
    if user is None or not password_is_valid:
        raise ApiError(ErrorCode.INVALID_CREDENTIALS, "Invalid email or password")

    if not user.is_active:
        raise ApiError(ErrorCode.ACCOUNT_DEACTIVATED, "Account has been deactivated")

    if not user.is_email_verified:
        raise ApiError(
            ErrorCode.EMAIL_NOT_VERIFIED, "Please verify your email before logging in"
        )

    return ApiResponse(data=_issue_tokens(user, response, db))


@router.post("/google", response_model=ApiResponse[LoginData])
@limiter.limit("5/minute")
def google_login(
    request: Request,
    payload: GoogleLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """Logs in via a Google ID token: links to an existing account by
    email, or creates a new Tourist account. Google-only forever - this
    never sets a password, and never lets a Google account log in any
    other way."""
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not google_client_id:
        raise ApiError(
            ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE, "Google sign-in is not configured"
        )

    try:
        claims = google_id_token.verify_oauth2_token(
            payload.id_token, google_requests.Request(), google_client_id
        )
    except ValueError as exc:
        raise ApiError(ErrorCode.INVALID_GOOGLE_TOKEN, "Google sign-in failed") from exc

    if not claims.get("email_verified", False):
        raise ApiError(
            ErrorCode.INVALID_GOOGLE_TOKEN, "Google account email is not verified"
        )

    google_id = claims["sub"]
    email = claims["email"].lower()

    user = db.query(User).filter(User.google_id == google_id).first()
    if user is None:
        user = db.query(User).filter(User.email == email).first()

    if user is not None and not user.is_active:
        raise ApiError(ErrorCode.ACCOUNT_DEACTIVATED, "Account has been deactivated")

    if user is None:
        user = User(
            full_name=claims.get("name") or email,
            email=email,
            login_provider="google",
            google_id=google_id,
        )
        db.add(user)
    elif user.google_id is None:
        user.google_id = google_id

    # Google has already proven this email, regardless of which path above.
    user.is_email_verified = True
    db.add(user)
    db.commit()
    db.refresh(user)

    return ApiResponse(data=_issue_tokens(user, response, db))


@router.post("/refresh", response_model=ApiResponse[RefreshData])
def refresh(
    response: Response,
    payload: RefreshRequest | None = None,
    refresh_token_cookie: str | None = Cookie(
        default=None, alias=REFRESH_TOKEN_COOKIE_NAME
    ),
    db: Session = Depends(get_db),
):
    """Exchange a valid refresh token for a new access/refresh pair.
    The old refresh token is invalidated in the same call.

    Web clients send the refresh token via the httpOnly cookie set on
    login; mobile clients (which can't rely on cookies) send it in the
    request body instead. The cookie takes precedence when both are
    present."""
    refresh_token = refresh_token_cookie or (
        payload.refresh_token if payload is not None else None
    )
    if refresh_token is None:
        raise ApiError(
            ErrorCode.INVALID_REFRESH_TOKEN, "Refresh token is invalid or expired"
        )

    try:
        claims = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
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
    token_hash = hash_refresh_token(refresh_token)
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
    _issue_refresh_token_cookie(response, new_refresh_token)

    return ApiResponse(
        data=RefreshData(access_token=access_token, refresh_token=new_refresh_token)
    )


@router.post("/logout", response_model=ApiResponse[dict])
def logout(
    response: Response,
    payload: LogoutRequest | None = None,
    refresh_token_cookie: str | None = Cookie(
        default=None, alias=REFRESH_TOKEN_COOKIE_NAME
    ),
    db: Session = Depends(get_db),
):
    """Clear both auth cookies and revoke the refresh token, so
    neither can be used again after logout."""
    refresh_token = refresh_token_cookie or (
        payload.refresh_token if payload is not None else None
    )
    if refresh_token is not None:
        token_hash = hash_refresh_token(refresh_token)
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
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
    )
    return ApiResponse(data={})


@router.post("/forgot-password", response_model=ApiResponse[dict])
@limiter.limit("5/minute")
def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """Sends a reset email only if the account has a password. Same
    generic response either way, so nothing about the account leaks."""
    user = db.query(User).filter(User.email == payload.email).first()

    if user is not None and user.password_hash is not None:
        _send_password_reset_email(user, db)

    return ApiResponse(data={})


@router.post("/reset-password", response_model=ApiResponse[dict])
@limiter.limit("5/minute")
def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """Sets a new password if the reset token is valid and unexpired,
    then revokes the account's refresh token - any other device must
    log in again with the new password. The token is cleared either
    way, so it can't be replayed."""
    user = db.query(User).filter(User.password_reset_token == payload.token).first()

    is_valid = (
        user is not None
        and user.reset_token_expiry is not None
        and user.reset_token_expiry > datetime.now(timezone.utc)
    )
    if not is_valid:
        raise ApiError(
            ErrorCode.INVALID_RESET_TOKEN, "Reset link is invalid or expired"
        )

    user.password_hash = hash_password(payload.new_password)
    user.password_reset_token = None
    user.reset_token_expiry = None
    user.refresh_token = None
    user.refresh_token_expiry = None
    db.add(user)
    db.commit()

    return ApiResponse(data={})


@router.post("/change-password", response_model=ApiResponse[LoginData])
def change_password(
    payload: ChangePasswordRequest,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the logged-in user's password. A Google-only account has
    none to check, so this rejects instead of crashing. Rotates the
    session's tokens on success, revoking any other device's session."""
    if current_user.password_hash is None or not verify_password(
        payload.current_password, current_user.password_hash
    ):
        raise ApiError(ErrorCode.INVALID_CREDENTIALS, "Current password is incorrect")

    current_user.password_hash = hash_password(payload.new_password)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return ApiResponse(data=_issue_tokens(current_user, response, db))


@router.post("/delete-account", response_model=ApiResponse[dict])
def delete_account(
    payload: DeleteAccountRequest,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Anonymizes and deactivates the account rather than deleting the
    row outright - trips and feedback reference it by foreign key, and
    a hard delete would fail (or silently orphan that history) instead
    of just working. Local accounts must confirm with their current
    password; Google-only accounts have none to confirm with."""
    if current_user.password_hash is not None and (
        payload.current_password is None
        or not verify_password(payload.current_password, current_user.password_hash)
    ):
        raise ApiError(ErrorCode.INVALID_CREDENTIALS, "Current password is incorrect")

    current_user.full_name = "Deleted User"
    # `.local`/`.invalid`/`.test` etc are reserved special-use TLDs that
    # EmailStr rejects outright - this domain just needs to be syntactically
    # ordinary, not real or deliverable.
    current_user.email = f"deleted-{current_user.id}@deleted-users.tripmate.com"
    current_user.password_hash = None
    current_user.google_id = None
    current_user.is_active = False
    current_user.email_verification_token = None
    current_user.email_verification_expiry = None
    current_user.password_reset_token = None
    current_user.reset_token_expiry = None
    current_user.refresh_token = None
    current_user.refresh_token_expiry = None
    current_user.preferred_travel_style = None
    current_user.preferred_accommodation = None
    current_user.typical_budget_range = None
    current_user.interests = None
    db.add(current_user)
    db.commit()

    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
    )
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
    )
    return ApiResponse(data={})
