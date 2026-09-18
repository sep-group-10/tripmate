"""Tests for POST /auth/verify-email and POST /auth/resend-verification."""

from datetime import datetime, timedelta, timezone

import pytest

from app.core.security import hash_password
from app.models.user import User

VERIFY_URL = "/api/v1/auth/verify-email"
RESEND_URL = "/api/v1/auth/resend-verification"
LOGIN_URL = "/api/v1/auth/login"

PASSWORD = "unverifiedpassword123"


@pytest.fixture(autouse=True)
def mock_send_email(monkeypatch):
    """Resend-verification sends a real email - stub it out so tests
    never depend on network access or real AWS credentials."""
    mock = MockSendEmail()
    monkeypatch.setattr("app.routers.auth.send_email", mock)
    return mock


class MockSendEmail:
    """Records calls instead of actually sending, so tests can assert
    whether an email was (or wasn't) triggered."""

    def __init__(self):
        self.calls = []

    def __call__(self, to, subject, body):
        self.calls.append((to, subject, body))
        return True


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


def test_resend_verification_generates_a_new_token(client, db_session):
    user = _create_unverified_user(db_session, token="old-token")

    response = client.post(RESEND_URL, json={"email": user.email})

    assert response.status_code == 200
    db_session.refresh(user)
    assert user.email_verification_token is not None
    assert user.email_verification_token != "old-token"
    assert user.is_email_verified is False


def test_resend_verification_sends_an_email(client, db_session, mock_send_email):
    user = _create_unverified_user(db_session, token="old-token")

    client.post(RESEND_URL, json={"email": user.email})

    assert len(mock_send_email.calls) == 1
    to, _subject, _body = mock_send_email.calls[0]
    assert to == user.email


def test_resend_verification_new_token_works_for_verify(client, db_session):
    user = _create_unverified_user(db_session, token="old-token")

    client.post(RESEND_URL, json={"email": user.email})
    db_session.refresh(user)
    new_token = user.email_verification_token

    response = client.post(VERIFY_URL, json={"token": new_token})

    assert response.status_code == 200


def test_resend_verification_old_token_stops_working(client, db_session):
    user = _create_unverified_user(db_session, token="old-token")

    client.post(RESEND_URL, json={"email": user.email})

    response = client.post(VERIFY_URL, json={"token": "old-token"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_VERIFICATION_TOKEN"


def test_resend_verification_for_already_verified_user_does_not_send(
    client, db_session, mock_send_email
):
    user = User(
        full_name="Already Verified",
        email="alreadyverified@example.com",
        password_hash=hash_password(PASSWORD),
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(RESEND_URL, json={"email": user.email})

    assert response.status_code == 200
    assert len(mock_send_email.calls) == 0


def test_resend_verification_for_unknown_email_returns_generic_success(
    client, mock_send_email
):
    response = client.post(RESEND_URL, json={"email": "nobody@example.com"})

    assert response.status_code == 200
    assert response.json()["data"] == {}
    assert len(mock_send_email.calls) == 0


def test_resend_verification_missing_email_returns_validation_error(client):
    response = client.post(RESEND_URL, json={})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
