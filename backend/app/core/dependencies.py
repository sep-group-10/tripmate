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

# auto_error=False so this scheme never blocks a request on its own.
# It exists only so Swagger UI shows an "Authorize" button and attaches
# the header for us; the actual extraction/validation happens below.
_bearer_scheme = HTTPBearer(auto_error=False)


def _extract_token(
    request: Request, credentials: HTTPAuthorizationCredentials | None
) -> str | None:
    """Return the access token from the Authorization header if present,
    otherwise fall back to the access_token cookie."""
    if credentials is not None:
        return credentials.credentials

    return request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency that resolves the authenticated user for a
    request, accepting either a Bearer token or the auth cookie.
    Raises ApiError (401/403) if the token is missing, invalid,
    expired, or belongs to a deactivated account."""
    token = _extract_token(request, credentials)
    if token is None:
        raise ApiError(ErrorCode.UNAUTHORIZED, "Authentication required")

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise ApiError(ErrorCode.TOKEN_EXPIRED, "Access token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise ApiError(ErrorCode.UNAUTHORIZED, "Invalid access token") from exc

    # Only accept access tokens here, so a refresh token can never be
    # used to authenticate a normal request.
    if payload.get("type") != "access":
        raise ApiError(ErrorCode.UNAUTHORIZED, "Invalid access token")

    try:
        user_id = uuid.UUID(payload.get("sub", ""))
    except ValueError as exc:
        raise ApiError(ErrorCode.UNAUTHORIZED, "Invalid access token") from exc

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise ApiError(ErrorCode.UNAUTHORIZED, "Invalid access token")

    # Checked on every request (not just at login) so a mid-session
    # deactivation takes effect immediately on the next call.
    if not user.is_active:
        raise ApiError(ErrorCode.ACCOUNT_DEACTIVATED, "Account has been deactivated")

    return user


def require_role(role: Role):
    """Dependency factory that builds a FastAPI dependency enforcing a
    minimum role on a route, e.g. Depends(require_role(Role.ADMIN)).
    Raises ApiError(FORBIDDEN) if the current user's role does not
    satisfy the required role (see roles.py for the inheritance rules)."""
    allowed_roles = roles_satisfying(role)

    def check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ApiError(
                ErrorCode.FORBIDDEN,
                "You do not have permission to access this resource",
            )
        return current_user

    return check_role
