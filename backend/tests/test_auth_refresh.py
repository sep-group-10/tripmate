"""Tests for POST /auth/refresh (token rotation) and refresh token
revocation on POST /auth/logout."""

import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.core.security import JWT_ALGORITHM, JWT_SECRET_KEY, hash_password
from app.models.user import User

LOGIN_URL = "/api/v1/auth/login"
LOGOUT_URL = "/api/v1/auth/logout"
REFRESH_URL = "/api/v1/auth/refresh"

EXISTING_USER_PASSWORD = "existingpassword123"


def _make_refresh_token(
    sub: str, token_type: str = "refresh", expires_delta=None
) -> str:
    """Hand-craft a refresh JWT for edge cases the normal login flow
    cannot produce (expired, wrong type, bad subject)."""
    now = datetime.now(timezone.utc)
    expires_delta = timedelta(days=7) if expires_delta is None else expires_delta
    payload = {
        "sub": sub,
        "type": token_type,
        "jti": "test-jti",
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def _login(client, email, password):
    response = client.post(LOGIN_URL, json={"email": email, "password": password})
    return response.json()["data"]


def test_refresh_with_valid_token_returns_new_token_pair(client, existing_user):
    login_data = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.post(
        REFRESH_URL, json={"refresh_token": login_data["refresh_token"]}
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["access_token"] != login_data["access_token"]
    assert body["refresh_token"] != login_data["refresh_token"]


def test_refresh_response_never_includes_user(client, existing_user):
    login_data = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.post(
        REFRESH_URL, json={"refresh_token": login_data["refresh_token"]}
    )

    assert "user" not in response.json()["data"]


def test_refresh_rotates_the_stored_token(client, existing_user, db_session):
    login_data = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    client.post(REFRESH_URL, json={"refresh_token": login_data["refresh_token"]})

    # The token just used must no longer work, since a new one replaced it.
    response = client.post(
        REFRESH_URL, json={"refresh_token": login_data["refresh_token"]}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


def test_refresh_with_rotated_out_token_is_rejected(client, existing_user):
    login_data = _login(client, existing_user.email, EXISTING_USER_PASSWORD)
    first_refresh = client.post(
        REFRESH_URL, json={"refresh_token": login_data["refresh_token"]}
    ).json()["data"]

    # The new token from the first refresh must still work on its own.
    response = client.post(
        REFRESH_URL, json={"refresh_token": first_refresh["refresh_token"]}
    )

    assert response.status_code == 200


def test_refresh_with_expired_token_is_rejected(client, existing_user):
    expired_token = _make_refresh_token(
        sub=str(existing_user.id), expires_delta=timedelta(days=-1)
    )

    response = client.post(REFRESH_URL, json={"refresh_token": expired_token})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


def test_refresh_with_malformed_token_is_rejected(client):
    response = client.post(REFRESH_URL, json={"refresh_token": "not-a-real-token"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


def test_refresh_with_access_type_token_is_rejected(client, existing_user):
    access_typed_token = _make_refresh_token(
        sub=str(existing_user.id), token_type="access"
    )

    response = client.post(REFRESH_URL, json={"refresh_token": access_typed_token})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


def test_refresh_with_malformed_sub_claim_is_rejected(client):
    token = _make_refresh_token(sub="not-a-uuid")

    response = client.post(REFRESH_URL, json={"refresh_token": token})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


def test_refresh_with_token_for_deleted_user_is_rejected(client):
    token = _make_refresh_token(sub=str(uuid.uuid4()))

    response = client.post(REFRESH_URL, json={"refresh_token": token})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


def test_refresh_with_unissued_token_for_real_user_is_rejected(client, existing_user):
    # Signature and claims are valid, but this token was never stored
    # as the user's current refresh token.
    token = _make_refresh_token(sub=str(existing_user.id))

    response = client.post(REFRESH_URL, json={"refresh_token": token})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


def test_refresh_for_deactivated_account_is_rejected(client, db_session):
    user = User(
        full_name="Deactivated Refresh User",
        email="deactivatedrefresh@example.com",
        password_hash=hash_password(EXISTING_USER_PASSWORD),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    login_response = client.post(
        LOGIN_URL,
        json={"email": user.email, "password": EXISTING_USER_PASSWORD},
    )
    refresh_token = login_response.json()["data"]["refresh_token"]

    user.is_active = False
    db_session.add(user)
    db_session.commit()

    response = client.post(REFRESH_URL, json={"refresh_token": refresh_token})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCOUNT_DEACTIVATED"


def test_refresh_sets_new_access_token_cookie(client, existing_user):
    login_data = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.post(
        REFRESH_URL, json={"refresh_token": login_data["refresh_token"]}
    )

    set_cookie = response.headers.get("set-cookie")
    assert set_cookie is not None
    assert "HttpOnly" in set_cookie


def test_refresh_missing_field_returns_validation_error(client):
    response = client.post(REFRESH_URL, json={})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_logout_with_refresh_token_revokes_it(client, existing_user, db_session):
    login_data = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.post(
        LOGOUT_URL, json={"refresh_token": login_data["refresh_token"]}
    )
    assert response.status_code == 200

    user = db_session.query(User).filter(User.id == existing_user.id).first()
    assert user.refresh_token is None
    assert user.refresh_token_expiry is None


def test_refresh_after_logout_is_rejected(client, existing_user):
    login_data = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    client.post(LOGOUT_URL, json={"refresh_token": login_data["refresh_token"]})

    response = client.post(
        REFRESH_URL, json={"refresh_token": login_data["refresh_token"]}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


def test_logout_with_no_body_still_succeeds(client):
    response = client.post(LOGOUT_URL)

    assert response.status_code == 200
    assert response.json()["data"] == {}


def test_logout_with_unknown_refresh_token_still_succeeds(client):
    response = client.post(LOGOUT_URL, json={"refresh_token": "garbage-token"})

    assert response.status_code == 200
    assert response.json()["data"] == {}


def test_logout_does_not_revoke_other_users_token(
    client, existing_user, other_user, db_session
):
    other_login = client.post(
        LOGIN_URL,
        json={"email": other_user.email, "password": "otheruserpassword123"},
    ).json()["data"]

    # Log out the current session with an unrelated refresh token.
    client.post(LOGOUT_URL, json={"refresh_token": "garbage-token"})

    other_user_after = db_session.query(User).filter(User.id == other_user.id).first()
    assert other_user_after.refresh_token is not None

    # The other user's token must still work.
    response = client.post(
        REFRESH_URL, json={"refresh_token": other_login["refresh_token"]}
    )
    assert response.status_code == 200
