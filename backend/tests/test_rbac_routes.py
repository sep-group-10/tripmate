"""Tests proving require_role works through a real HTTP request (login
-> token -> route), not just as a direct function call. No admin route
exists in the app yet, so a throwaway one is attached for these tests
only (see admin_only_test_route below)."""

import pytest
from fastapi import Depends

from app.core.dependencies import require_role
from app.core.roles import Role
from app.core.security import hash_password
from app.main import app
from app.models.user import User

LOGIN_URL = "/api/v1/auth/login"
ADMIN_ROUTE = "/api/v1/_test_admin_only_route"

TEST_PASSWORD = "testpassword123"


@pytest.fixture(autouse=True)
def admin_only_test_route():
    """Attaches a throwaway route guarded by require_role(ADMIN) to the
    real app, so these tests exercise the actual FastAPI dependency
    pipeline and exception handlers rather than calling require_role
    directly. Removed after each test so it never leaks into the app
    used by other test files.
    """

    require_admin = require_role(Role.ADMIN)

    @app.get(ADMIN_ROUTE)
    def admin_only(current_user: User = Depends(require_admin)):
        return {"role": current_user.role}

    yield

    app.router.routes = [
        route
        for route in app.router.routes
        if getattr(route, "path", None) != ADMIN_ROUTE
    ]


def _create_user_with_role(db_session, email: str, role: str) -> User:
    """Create and persist a user with a specific role for RBAC tests."""
    user = User(
        full_name="RBAC Test User",
        email=email,
        password_hash=hash_password(TEST_PASSWORD),
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _login(client, email: str) -> str:
    """Log in and return just the access token."""
    response = client.post(LOGIN_URL, json={"email": email, "password": TEST_PASSWORD})
    return response.json()["data"]["access_token"]


def test_tourist_is_blocked_from_admin_route(client, db_session):
    user = _create_user_with_role(db_session, "tourist@example.com", "TOURIST")
    token = _login(client, user.email)

    response = client.get(ADMIN_ROUTE, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_admin_is_allowed_on_admin_route(client, db_session):
    user = _create_user_with_role(db_session, "admin@example.com", "ADMIN")
    token = _login(client, user.email)

    response = client.get(ADMIN_ROUTE, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["role"] == "ADMIN"


def test_super_admin_is_allowed_on_admin_route(client, db_session):
    user = _create_user_with_role(db_session, "superadmin@example.com", "SUPER_ADMIN")
    token = _login(client, user.email)

    response = client.get(ADMIN_ROUTE, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["role"] == "SUPER_ADMIN"


def test_unauthenticated_request_is_blocked_from_admin_route(client):
    response = client.get(ADMIN_ROUTE)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
