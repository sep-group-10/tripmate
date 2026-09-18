"""Tests for POST /auth/google."""

from unittest.mock import patch

from app.core.security import hash_password, verify_password
from app.models.user import User

GOOGLE_URL = "/api/v1/auth/google"


def _mock_google(claims):
    return patch(
        "app.routers.auth.google_id_token.verify_oauth2_token", return_value=claims
    )


def test_google_login_creates_new_tourist_account(client, db_session):
    claims = {
        "sub": "google-sub-1",
        "email": "newgoogleuser@example.com",
        "email_verified": True,
        "name": "New Google User",
    }

    with _mock_google(claims):
        response = client.post(GOOGLE_URL, json={"id_token": "fake"})

    assert response.status_code == 200
    body = response.json()["data"]
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["user"]["email"] == "newgoogleuser@example.com"
    assert body["user"]["role"] == "TOURIST"
    assert body["user"]["login_provider"] == "google"
    assert body["user"]["is_email_verified"] is True

    user = (
        db_session.query(User).filter(User.email == "newgoogleuser@example.com").first()
    )
    assert user.google_id == "google-sub-1"
    assert user.password_hash is None


def test_google_login_links_existing_local_account(client, db_session):
    local_user = User(
        full_name="Local Account",
        email="linktest@example.com",
        password_hash=hash_password("LocalPass1"),
        is_email_verified=False,
    )
    db_session.add(local_user)
    db_session.commit()

    claims = {
        "sub": "google-sub-2",
        "email": "linktest@example.com",
        "email_verified": True,
        "name": "Local Account",
    }

    with _mock_google(claims):
        response = client.post(GOOGLE_URL, json={"id_token": "fake"})

    assert response.status_code == 200
    db_session.refresh(local_user)
    assert local_user.google_id == "google-sub-2"
    assert local_user.is_email_verified is True
    assert local_user.login_provider == "local"
    assert verify_password("LocalPass1", local_user.password_hash)


def test_google_login_second_time_reuses_same_account(client, db_session):
    claims = {
        "sub": "google-sub-3",
        "email": "repeatgoogle@example.com",
        "email_verified": True,
        "name": "Repeat User",
    }

    with _mock_google(claims):
        client.post(GOOGLE_URL, json={"id_token": "fake"})
        response = client.post(GOOGLE_URL, json={"id_token": "fake"})

    assert response.status_code == 200
    count = (
        db_session.query(User).filter(User.email == "repeatgoogle@example.com").count()
    )
    assert count == 1


def test_google_login_for_deactivated_account_is_rejected(client, db_session):
    user = User(
        full_name="Deactivated",
        email="deactivatedgoogle@example.com",
        password_hash=hash_password("Pass1234"),
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()

    claims = {
        "sub": "google-sub-4",
        "email": "deactivatedgoogle@example.com",
        "email_verified": True,
        "name": "Deactivated",
    }

    with _mock_google(claims):
        response = client.post(GOOGLE_URL, json={"id_token": "fake"})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCOUNT_DEACTIVATED"


def test_google_login_with_unverified_email_claim_is_rejected(client):
    claims = {
        "sub": "google-sub-5",
        "email": "sneaky@example.com",
        "email_verified": False,
        "name": "Sneaky",
    }

    with _mock_google(claims):
        response = client.post(GOOGLE_URL, json={"id_token": "fake"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_GOOGLE_TOKEN"


def test_google_login_with_invalid_token_is_rejected(client):
    with patch(
        "app.routers.auth.google_id_token.verify_oauth2_token",
        side_effect=ValueError("bad token"),
    ):
        response = client.post(GOOGLE_URL, json={"id_token": "garbage"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_GOOGLE_TOKEN"


def test_google_login_missing_id_token_returns_validation_error(client):
    response = client.post(GOOGLE_URL, json={})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_local_login_with_google_only_account_fails_gracefully(client, db_session):
    """A Google-only account has no password_hash - login() must treat
    this as a normal wrong-password failure, not crash."""
    user = User(
        full_name="Google Only",
        email="googleonly@example.com",
        login_provider="google",
        google_id="google-sub-6",
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "anypassword1"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"
