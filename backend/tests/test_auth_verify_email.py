"""Tests for POST /auth/verify-email."""

from datetime import datetime, timedelta, timezone

from app.core.security import hash_password
from app.models.user import User

VERIFY_URL = "/api/v1/auth/verify-email"
LOGIN_URL = "/api/v1/auth/login"

PASSWORD = "unverifiedpassword123"


def _create_unverified_user(db_session, token: str, expires_delta=None) -> User:
    expires_delta = timedelta(hours=24) if expires_delta is None else expires_delta
    user = User(
        full_name="Unverified User",
        email="verifyme@example.com",
        password_hash=hash_password(PASSWORD),
        email_verification_token=token,
        email_verification_expiry=datetime.now(timezone.utc) + expires_delta,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_verify_email_with_valid_token_succeeds(client, db_session):
    user = _create_unverified_user(db_session, token="valid-token-123")

    response = client.post(VERIFY_URL, json={"token": "valid-token-123"})

    assert response.status_code == 200
    db_session.refresh(user)
    assert user.is_email_verified is True


def test_verify_email_clears_the_token(client, db_session):
    user = _create_unverified_user(db_session, token="valid-token-123")

    client.post(VERIFY_URL, json={"token": "valid-token-123"})

    db_session.refresh(user)
    assert user.email_verification_token is None
    assert user.email_verification_expiry is None


def test_verify_email_token_is_single_use(client, db_session):
    _create_unverified_user(db_session, token="valid-token-123")

    first = client.post(VERIFY_URL, json={"token": "valid-token-123"})
    second = client.post(VERIFY_URL, json={"token": "valid-token-123"})

    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["error"]["code"] == "INVALID_VERIFICATION_TOKEN"


def test_verify_email_with_garbage_token_is_rejected(client):
    response = client.post(VERIFY_URL, json={"token": "not-a-real-token"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_VERIFICATION_TOKEN"


def test_verify_email_with_expired_token_is_rejected(client, db_session):
    _create_unverified_user(
        db_session, token="expired-token", expires_delta=timedelta(hours=-1)
    )

    response = client.post(VERIFY_URL, json={"token": "expired-token"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_VERIFICATION_TOKEN"


def test_verify_email_missing_token_returns_validation_error(client):
    response = client.post(VERIFY_URL, json={})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_login_succeeds_after_verification(client, db_session):
    user = _create_unverified_user(db_session, token="valid-token-123")

    client.post(VERIFY_URL, json={"token": "valid-token-123"})

    response = client.post(LOGIN_URL, json={"email": user.email, "password": PASSWORD})

    assert response.status_code == 200
