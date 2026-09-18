"""Tests for POST /auth/forgot-password."""

import pytest

FORGOT_URL = "/api/v1/auth/forgot-password"


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
    """Forgot-password sends a real email - stub it out so tests never
    depend on network access or real AWS credentials."""
    mock = MockSendEmail()
    monkeypatch.setattr("app.routers.auth.send_email", mock)
    return mock


def test_forgot_password_for_known_email_sends_reset_email(
    client, existing_user, mock_send_email
):
    response = client.post(FORGOT_URL, json={"email": existing_user.email})

    assert response.status_code == 200
    assert response.json()["data"] == {}
    assert len(mock_send_email.calls) == 1
    to, _subject, _body = mock_send_email.calls[0]
    assert to == existing_user.email


def test_forgot_password_generates_a_reset_token(client, existing_user, db_session):
    client.post(FORGOT_URL, json={"email": existing_user.email})

    db_session.refresh(existing_user)
    assert existing_user.password_reset_token is not None
    assert existing_user.reset_token_expiry is not None


def test_forgot_password_for_unknown_email_returns_generic_success(
    client, mock_send_email
):
    response = client.post(FORGOT_URL, json={"email": "nobody@example.com"})

    assert response.status_code == 200
    assert response.json()["data"] == {}
    assert len(mock_send_email.calls) == 0


def test_forgot_password_missing_email_returns_validation_error(client):
    response = client.post(FORGOT_URL, json={})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_forgot_password_normalizes_email_case(client, existing_user, mock_send_email):
    response = client.post(FORGOT_URL, json={"email": existing_user.email.upper()})

    assert response.status_code == 200
    assert len(mock_send_email.calls) == 1
