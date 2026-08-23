import uuid

import jwt
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import ApiError, ErrorCode
from app.core.security import (
    ACCESS_TOKEN_COOKIE_NAME,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)
from app.models.user import User


def _extract_token(request: Request) -> str | None:
    authorization = request.headers.get("Authorization")
    if authorization is not None:
        scheme, _, credentials = authorization.partition(" ")
        if scheme.lower() == "bearer" and credentials:
            return credentials

    return request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = _extract_token(request)
    if token is None:
        raise ApiError(ErrorCode.UNAUTHORIZED, "Authentication required")

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise ApiError(ErrorCode.TOKEN_EXPIRED, "Access token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise ApiError(ErrorCode.UNAUTHORIZED, "Invalid access token") from exc

    if payload.get("type") != "access":
        raise ApiError(ErrorCode.UNAUTHORIZED, "Invalid access token")

    try:
        user_id = uuid.UUID(payload.get("sub", ""))
    except ValueError as exc:
        raise ApiError(ErrorCode.UNAUTHORIZED, "Invalid access token") from exc

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise ApiError(ErrorCode.UNAUTHORIZED, "Invalid access token")

    if not user.is_active:
        raise ApiError(ErrorCode.ACCOUNT_DEACTIVATED, "Account has been deactivated")

    return user
