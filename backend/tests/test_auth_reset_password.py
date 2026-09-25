"""Tests for POST /auth/reset-password."""

from datetime import datetime, timedelta, timezone

from app.core.security import hash_password, verify_password
from app.models.user import User

RESET_URL = "/api/v1/auth/reset-password"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"

OLD_PASSWORD = "oldpassword123"
NEW_PASSWORD = "newpassword456"


def _create_user_with_reset_token(
    db_session, token: str, expires_delta=None, **overrides
) -> User:
    expires_delta = timedelta(minutes=15) if expires_delta is None else expires_delta
    user = User(
        full_name="Reset Me",
        email="resetme@example.com",
        password_hash=hash_password(OLD_PASSWORD),
        is_email_verified=True,
        password_reset_token=token,
        reset_token_expiry=datetime.now(timezone.utc) + expires_delta,
        **overrides,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_reset_password_with_valid_token_updates_hash(client, db_session):
    user = _create_user_with_reset_token(db_session, token="valid-token")

    response = client.post(
        RESET_URL, json={"token": "valid-token", "new_password": NEW_PASSWORD}
    )

    assert response.status_code == 200
    db_session.refresh(user)
    assert verify_password(NEW_PASSWORD, user.password_hash)
    assert not verify_password(OLD_PASSWORD, user.password_hash)


def test_reset_password_clears_the_token(client, db_session):
    user = _create_user_with_reset_token(db_session, token="valid-token")

    client.post(RESET_URL, json={"token": "valid-token", "new_password": NEW_PASSWORD})

    db_session.refresh(user)
    assert user.password_reset_token is None
    assert user.reset_token_expiry is None


def test_reset_password_token_is_single_use(client, db_session):
    _create_user_with_reset_token(db_session, token="valid-token")

    first = client.post(
        RESET_URL, json={"token": "valid-token", "new_password": NEW_PASSWORD}
    )
    second = client.post(
        RESET_URL, json={"token": "valid-token", "new_password": "anotherpass789"}
    )

    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["error"]["code"] == "INVALID_RESET_TOKEN"


def test_reset_password_with_garbage_token_is_rejected(client):
    response = client.post(
        RESET_URL, json={"token": "not-a-real-token", "new_password": NEW_PASSWORD}
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_RESET_TOKEN"


def test_reset_password_with_expired_token_is_rejected(client, db_session):
    _create_user_with_reset_token(
        db_session, token="expired-token", expires_delta=timedelta(minutes=-1)
    )

    response = client.post(
        RESET_URL, json={"token": "expired-token", "new_password": NEW_PASSWORD}
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_RESET_TOKEN"


def test_reset_password_with_weak_new_password_is_rejected(client, db_session):
    _create_user_with_reset_token(db_session, token="valid-token")

    response = client.post(
        RESET_URL, json={"token": "valid-token", "new_password": "nodigitshere"}
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_reset_password_missing_fields_returns_validation_error(client):
    response = client.post(RESET_URL, json={})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_login_with_old_password_fails_after_reset(client, db_session):
    user = _create_user_with_reset_token(db_session, token="valid-token")

    client.post(RESET_URL, json={"token": "valid-token", "new_password": NEW_PASSWORD})

    response = client.post(
        LOGIN_URL, json={"email": user.email, "password": OLD_PASSWORD}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_with_new_password_succeeds_after_reset(client, db_session):
    user = _create_user_with_reset_token(db_session, token="valid-token")

    client.post(RESET_URL, json={"token": "valid-token", "new_password": NEW_PASSWORD})

    response = client.post(
        LOGIN_URL, json={"email": user.email, "password": NEW_PASSWORD}
    )

    assert response.status_code == 200


def test_reset_password_revokes_existing_refresh_token(client, db_session):
    user = _create_user_with_reset_token(db_session, token="valid-token")
    login_data = client.post(
        LOGIN_URL, json={"email": user.email, "password": OLD_PASSWORD}
    ).json()["data"]

    client.cookies.clear()
    client.post(RESET_URL, json={"token": "valid-token", "new_password": NEW_PASSWORD})

    response = client.post(
        REFRESH_URL, json={"refresh_token": login_data["refresh_token"]}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"
