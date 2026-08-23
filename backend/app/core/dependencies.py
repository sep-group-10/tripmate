import uuid

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import ApiError, ErrorCode
from app.core.roles import Role, roles_satisfying
from app.core.security import (
    ACCESS_TOKEN_COOKIE_NAME,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)
from app.models.user import User

# auto_error=False: this scheme only exists so Swagger UI shows an
# "Authorize" button and attaches the header for us. The real
# extraction/validation (bearer header OR cookie) happens below.
_bearer_scheme = HTTPBearer(auto_error=False)


def _extract_token(
    request: Request, credentials: HTTPAuthorizationCredentials | None
) -> str | None:
    if credentials is not None:
        return credentials.credentials

    return request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = _extract_token(request, credentials)
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


def require_role(role: Role):
    allowed_roles = roles_satisfying(role)

    def check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ApiError(
                ErrorCode.FORBIDDEN,
                "You do not have permission to access this resource",
            )
        return current_user

    return check_role
