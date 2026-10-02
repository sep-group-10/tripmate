"""Tests for POST /admin/admins and GET /admin/admins."""

import pytest

from app.core.security import hash_password
from app.models.user import User

CREATE_ADMIN_URL = "/api/v1/admin/admins"
LIST_ADMINS_URL = "/api/v1/admin/admins"
RESET_PASSWORD_URL = "/api/v1/auth/reset-password"


class MockSendEmail:
    """Records calls instead of actually sending, so tests can assert
    whether an email was (or wasn't) triggered."""

    def __init__(self):
        self.calls = []

    def __call__(self, to, subject, body):
        self.calls.append((to, subject, body))
        return True


@pytest.fixture(autouse=True)
def mock_send_email(monkeypatch):
    """Admin creation sends a real email - stub it out so tests never
    depend on network access or real AWS credentials."""
    mock = MockSendEmail()
    monkeypatch.setattr("app.routers.admin.send_email", mock)
    return mock


def test_create_admin_requires_authentication(client):
    response = client.post(
        CREATE_ADMIN_URL,
        json={"full_name": "New Admin", "email": "new-admin@example.com"},
    )

    assert response.status_code == 401


def test_create_admin_blocked_for_plain_admin(admin_client):
    response = admin_client.post(
        CREATE_ADMIN_URL,
        json={"full_name": "New Admin", "email": "new-admin@example.com"},
    )

    assert response.status_code == 403


def test_create_admin_blocked_for_tourist(client, existing_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": existing_user.email, "password": "existingpassword123"},
    )
    token = response.json()["data"]["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.post(
        CREATE_ADMIN_URL,
        json={"full_name": "New Admin", "email": "new-admin@example.com"},
    )

    assert response.status_code == 403


def test_superadmin_can_create_admin(superadmin_client, db_session, mock_send_email):
    response = superadmin_client.post(
        CREATE_ADMIN_URL,
        json={
            "full_name": "New Admin",
            "email": "new-admin@example.com",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "new-admin@example.com"

    created = (
        db_session.query(User).filter(User.email == "new-admin@example.com").first()
    )
    assert created is not None
    assert created.role == "ADMIN"
    assert created.is_active is True
    assert created.is_email_verified is True
    assert created.password_hash is None
    assert created.password_reset_token is not None
    assert created.reset_token_expiry is not None

    assert len(mock_send_email.calls) == 1
    to, subject, body_text = mock_send_email.calls[0]
    assert to == "new-admin@example.com"
    assert "admin" in subject.lower()
    assert created.password_reset_token in body_text


def test_create_admin_ignores_role_in_request_body(superadmin_client, db_session):
    """The system has exactly one super admin - a role field in the
    request, if sent, must never let a caller create another one."""
    response = superadmin_client.post(
        CREATE_ADMIN_URL,
        json={
            "full_name": "Attempted Super Admin",
            "email": "attempted-superadmin@example.com",
            "role": "SUPER_ADMIN",
        },
    )

    assert response.status_code == 201
    created = (
        db_session.query(User)
        .filter(User.email == "attempted-superadmin@example.com")
        .first()
    )
    assert created.role == "ADMIN"


def test_create_admin_rejects_duplicate_email(superadmin_client, existing_user):
    response = superadmin_client.post(
        CREATE_ADMIN_URL,
        json={"full_name": "Dup", "email": existing_user.email},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_invited_admin_can_set_password_via_reset_password(
    superadmin_client, db_session
):
    superadmin_client.post(
        CREATE_ADMIN_URL,
        json={"full_name": "New Admin", "email": "new-admin2@example.com"},
    )
    created = (
        db_session.query(User).filter(User.email == "new-admin2@example.com").first()
    )
    token = created.password_reset_token

    response = superadmin_client.post(
        RESET_PASSWORD_URL,
        json={"token": token, "new_password": "brandnewpass123"},
    )

    assert response.status_code == 200

    db_session.refresh(created)
    assert created.password_hash is not None
    assert created.password_reset_token is None
    assert created.reset_token_expiry is None

    login_response = superadmin_client.post(
        "/api/v1/auth/login",
        json={"email": created.email, "password": "brandnewpass123"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["data"]["user"]["role"] == "ADMIN"


def test_list_admins_blocked_for_plain_admin(admin_client):
    response = admin_client.get(LIST_ADMINS_URL)

    assert response.status_code == 403


def test_list_admins_excludes_tourists(superadmin_client, db_session, existing_user):
    response = superadmin_client.get(LIST_ADMINS_URL)

    assert response.status_code == 200
    emails = [item["email"] for item in response.json()["data"]["items"]]
    assert existing_user.email not in emails
    assert "tourism-superadmin@example.com" in emails


def test_list_admins_filters_by_search(superadmin_client, db_session):
    other_admin = User(
        full_name="Searchable Admin",
        email="searchable-admin@example.com",
        password_hash=hash_password("somepassword123"),
        role="ADMIN",
        is_email_verified=True,
    )
    db_session.add(other_admin)
    db_session.commit()

    response = superadmin_client.get(LIST_ADMINS_URL, params={"q": "Searchable"})

    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["email"] == "searchable-admin@example.com"


def _status_url(admin_id):
    return f"/api/v1/admin/admins/{admin_id}/status"


def _create_plain_admin(db_session, email="plain-admin@example.com"):
    admin = User(
        full_name="Plain Admin",
        email=email,
        password_hash=hash_password("adminpassword123"),
        role="ADMIN",
        is_email_verified=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


def test_update_admin_status_blocked_for_plain_admin(admin_client, db_session):
    target = _create_plain_admin(db_session)

    response = admin_client.patch(_status_url(target.id), json={"is_active": False})

    assert response.status_code == 403


def test_superadmin_can_deactivate_admin(superadmin_client, db_session):
    target = _create_plain_admin(db_session)

    response = superadmin_client.patch(
        _status_url(target.id), json={"is_active": False}
    )

    assert response.status_code == 200
    db_session.refresh(target)
    assert target.is_active is False


def test_superadmin_can_reactivate_admin(superadmin_client, db_session):
    target = _create_plain_admin(db_session)
    target.is_active = False
    db_session.add(target)
    db_session.commit()

    response = superadmin_client.patch(_status_url(target.id), json={"is_active": True})

    assert response.status_code == 200
    db_session.refresh(target)
    assert target.is_active is True


def test_superadmin_cannot_deactivate_self(superadmin_client, db_session):
    self_user = (
        db_session.query(User)
        .filter(User.email == "tourism-superadmin@example.com")
        .first()
    )

    response = superadmin_client.patch(
        _status_url(self_user.id), json={"is_active": False}
    )

    assert response.status_code == 403


def test_superadmin_cannot_deactivate_other_superadmin(superadmin_client, db_session):
    other_superadmin = User(
        full_name="Other Super Admin",
        email="other-superadmin@example.com",
        password_hash=hash_password("superadminpassword123"),
        role="SUPER_ADMIN",
        is_email_verified=True,
    )
    db_session.add(other_superadmin)
    db_session.commit()
    db_session.refresh(other_superadmin)

    response = superadmin_client.patch(
        _status_url(other_superadmin.id), json={"is_active": False}
    )

    assert response.status_code == 403


def test_update_admin_status_404_for_unknown_id(superadmin_client):
    response = superadmin_client.patch(
        _status_url("00000000-0000-0000-0000-000000000000"), json={"is_active": False}
    )

    assert response.status_code == 404
