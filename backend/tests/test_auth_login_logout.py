import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.core.security import (
    ACCESS_TOKEN_COOKIE_NAME,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    hash_password,
)
from app.models.user import User

LOGIN_URL = "/api/v1/auth/login"
LOGOUT_URL = "/api/v1/auth/logout"
ME_URL = "/api/v1/auth/me"

EXISTING_USER_PASSWORD = "existingpassword123"


def _make_token(sub: str, token_type: str = "access", expires_delta=None) -> str:
    now = datetime.now(timezone.utc)
    expires_delta = timedelta(minutes=15) if expires_delta is None else expires_delta
    payload = {
        "sub": sub,
        "role": "TOURIST",
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def test_login_success_returns_200_with_token_and_user(client, existing_user):
    response = client.post(
        LOGIN_URL,
        json={"email": existing_user.email, "password": EXISTING_USER_PASSWORD},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert body["data"]["user"]["email"] == existing_user.email
    assert "password" not in body["data"]["user"]
    assert "password_hash" not in body["data"]["user"]


def test_login_success_sets_httponly_cookie(client, existing_user):
    response = client.post(
        LOGIN_URL,
        json={"email": existing_user.email, "password": EXISTING_USER_PASSWORD},
    )

    set_cookie = response.headers.get("set-cookie")
    assert set_cookie is not None
    assert ACCESS_TOKEN_COOKIE_NAME in set_cookie
    assert "HttpOnly" in set_cookie


def test_login_wrong_password_returns_401(client, existing_user):
    response = client.post(
        LOGIN_URL,
        json={"email": existing_user.email, "password": "wrongpassword"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_nonexistent_email_returns_401(client):
    response = client.post(
        LOGIN_URL,
        json={"email": "doesnotexist@example.com", "password": "whatever123"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_nonexistent_email_and_wrong_password_have_identical_errors(
    client, existing_user
):
    wrong_password_response = client.post(
        LOGIN_URL,
        json={"email": existing_user.email, "password": "wrongpassword"},
    )
    nonexistent_email_response = client.post(
        LOGIN_URL,
        json={"email": "doesnotexist@example.com", "password": "wrongpassword"},
    )

    assert wrong_password_response.json() == nonexistent_email_response.json()
    assert wrong_password_response.status_code == nonexistent_email_response.status_code


def test_login_deactivated_account_returns_forbidden(client, db_session):
    user = User(
        full_name="Deactivated User",
        email="deactivated@example.com",
        password_hash=hash_password(EXISTING_USER_PASSWORD),
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        LOGIN_URL,
        json={"email": user.email, "password": EXISTING_USER_PASSWORD},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCOUNT_DEACTIVATED"


def test_login_missing_fields_returns_validation_error(client):
    response = client.post(LOGIN_URL, json={"email": "missing@example.com"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_protected_route_without_token_returns_401(client):
    response = client.get(ME_URL)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_protected_route_with_invalid_token_returns_401(client):
    response = client.get(ME_URL, headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_protected_route_with_bearer_token_succeeds(client, existing_user):
    login_response = client.post(
        LOGIN_URL,
        json={"email": existing_user.email, "password": EXISTING_USER_PASSWORD},
    )
    token = login_response.json()["data"]["access_token"]

    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["data"]["email"] == existing_user.email


def test_protected_route_with_cookie_succeeds(client, existing_user):
    client.post(
        LOGIN_URL,
        json={"email": existing_user.email, "password": EXISTING_USER_PASSWORD},
    )

    response = client.get(ME_URL)

    assert response.status_code == 200
    assert response.json()["data"]["email"] == existing_user.email


def test_logout_returns_200_with_empty_data(client):
    response = client.post(LOGOUT_URL)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == {}


def test_logout_clears_the_cookie(client, existing_user):
    client.post(
        LOGIN_URL,
        json={"email": existing_user.email, "password": EXISTING_USER_PASSWORD},
    )
    assert client.cookies.get(ACCESS_TOKEN_COOKIE_NAME) is not None

    client.post(LOGOUT_URL)

    assert client.cookies.get(ACCESS_TOKEN_COOKIE_NAME) is None


def test_access_denied_after_logout(client, existing_user):
    client.post(
        LOGIN_URL,
        json={"email": existing_user.email, "password": EXISTING_USER_PASSWORD},
    )
    client.post(LOGOUT_URL)

    response = client.get(ME_URL)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_protected_route_with_expired_token_returns_token_expired(
    client, existing_user
):
    expired_token = _make_token(
        sub=str(existing_user.id), expires_delta=timedelta(minutes=-1)
    )

    response = client.get(ME_URL, headers={"Authorization": f"Bearer {expired_token}"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "TOKEN_EXPIRED"


def test_protected_route_with_refresh_type_token_returns_401(client, existing_user):
    refresh_typed_token = _make_token(sub=str(existing_user.id), token_type="refresh")

    response = client.get(
        ME_URL, headers={"Authorization": f"Bearer {refresh_typed_token}"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_protected_route_with_malformed_sub_claim_returns_401(client):
    token = _make_token(sub="not-a-uuid")

    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_protected_route_with_token_for_deleted_user_returns_401(client):
    token = _make_token(sub=str(uuid.uuid4()))

    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_protected_route_denies_access_after_mid_session_deactivation(
    client, existing_user, db_session
):
    login_response = client.post(
        LOGIN_URL,
        json={"email": existing_user.email, "password": EXISTING_USER_PASSWORD},
    )
    token = login_response.json()["data"]["access_token"]

    existing_user.is_active = False
    db_session.add(existing_user)
    db_session.commit()

    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCOUNT_DEACTIVATED"


def test_login_email_is_case_insensitive(client, existing_user):
    response = client.post(
        LOGIN_URL,
        json={
            "email": existing_user.email.upper(),
            "password": EXISTING_USER_PASSWORD,
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["user"]["email"] == existing_user.email


def test_login_rejects_non_string_password_type(client, existing_user):
    response = client.post(
        LOGIN_URL,
        json={"email": existing_user.email, "password": 12345678},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
