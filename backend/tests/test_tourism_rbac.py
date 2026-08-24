"""Tests for role-based access to tourism write endpoints."""

import uuid

from app.core.security import hash_password
from app.models.user import User

TEST_PASSWORD = "testpassword123"
LOGIN_URL = "/api/v1/auth/login"

DESTINATION_ID = "83f7d353-8731-4663-8e79-1a54d473f6dd"


def _create_user_with_role(db_session, email: str, role: str) -> User:
    """Create and persist a user with the requested role."""
    user = User(
        full_name="Tourism RBAC Test User",
        email=email,
        password_hash=hash_password(TEST_PASSWORD),
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _login(client, email: str) -> str:
    """Log in and return the access token."""
    response = client.post(
        LOGIN_URL,
        json={
            "email": email,
            "password": TEST_PASSWORD,
        },
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _destination_payload() -> dict:
    return {
        "name": f"RBAC Destination {uuid.uuid4()}",
        "description": "RBAC test destination",
        "country": "Sri Lanka",
        "region": "Central Province",
        "latitude": 7.2906,
        "longitude": 80.6337,
        "is_active": True,
    }


def test_tourist_is_blocked_from_creating_destination(client, db_session):
    user = _create_user_with_role(
        db_session,
        f"tourist-{uuid.uuid4()}@example.com",
        "TOURIST",
    )
    token = _login(client, user.email)

    response = client.post(
        "/api/v1/destinations",
        json=_destination_payload(),
        headers=_auth_headers(token),
    )

    assert response.status_code == 403


def test_admin_can_create_destination(client, db_session):
    user = _create_user_with_role(
        db_session,
        f"admin-{uuid.uuid4()}@example.com",
        "ADMIN",
    )
    token = _login(client, user.email)

    response = client.post(
        "/api/v1/destinations",
        json=_destination_payload(),
        headers=_auth_headers(token),
    )

    assert response.status_code == 201
