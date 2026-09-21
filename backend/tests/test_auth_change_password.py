"""Tests for POST /auth/change-password."""

from app.core.security import create_access_token, verify_password
from app.models.user import User

LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
CHANGE_PASSWORD_URL = "/api/v1/auth/change-password"

EXISTING_USER_PASSWORD = "existingpassword123"
NEW_PASSWORD = "newpassword456"


def _login(client, email, password):
    response = client.post(LOGIN_URL, json={"email": email, "password": password})
    return response.json()["data"]


def test_change_password_requires_authentication(client):
    response = client.post(
        CHANGE_PASSWORD_URL,
        json={"current_password": "whatever", "new_password": NEW_PASSWORD},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_change_password_with_wrong_current_password_is_rejected(client, existing_user):
    _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.post(
        CHANGE_PASSWORD_URL,
        json={"current_password": "wrongpassword1", "new_password": NEW_PASSWORD},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_change_password_with_weak_new_password_is_rejected(client, existing_user):
    _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.post(
        CHANGE_PASSWORD_URL,
        json={
            "current_password": EXISTING_USER_PASSWORD,
            "new_password": "nodigitshere",
        },
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_change_password_missing_fields_returns_validation_error(client, existing_user):
    _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.post(CHANGE_PASSWORD_URL, json={})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_change_password_success_updates_hash(client, existing_user, db_session):
    _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.post(
        CHANGE_PASSWORD_URL,
        json={
            "current_password": EXISTING_USER_PASSWORD,
            "new_password": NEW_PASSWORD,
        },
    )

    assert response.status_code == 200
    user = db_session.query(User).filter(User.id == existing_user.id).first()
    assert verify_password(NEW_PASSWORD, user.password_hash)
    assert not verify_password(EXISTING_USER_PASSWORD, user.password_hash)


def test_old_password_no_longer_logs_in_after_change(client, existing_user):
    _login(client, existing_user.email, EXISTING_USER_PASSWORD)
    client.post(
        CHANGE_PASSWORD_URL,
        json={
            "current_password": EXISTING_USER_PASSWORD,
            "new_password": NEW_PASSWORD,
        },
    )

    response = client.post(
        LOGIN_URL,
        json={"email": existing_user.email, "password": EXISTING_USER_PASSWORD},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_new_password_logs_in_after_change(client, existing_user):
    _login(client, existing_user.email, EXISTING_USER_PASSWORD)
    client.post(
        CHANGE_PASSWORD_URL,
        json={
            "current_password": EXISTING_USER_PASSWORD,
            "new_password": NEW_PASSWORD,
        },
    )

    response = client.post(
        LOGIN_URL,
        json={"email": existing_user.email, "password": NEW_PASSWORD},
    )

    assert response.status_code == 200


def test_change_password_returns_new_token_pair(client, existing_user):
    login_data = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.post(
        CHANGE_PASSWORD_URL,
        json={
            "current_password": EXISTING_USER_PASSWORD,
            "new_password": NEW_PASSWORD,
        },
    )

    body = response.json()["data"]
    assert body["access_token"] != login_data["access_token"]
    assert body["refresh_token"] != login_data["refresh_token"]


def test_change_password_sets_new_cookies(client, existing_user):
    _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.post(
        CHANGE_PASSWORD_URL,
        json={
            "current_password": EXISTING_USER_PASSWORD,
            "new_password": NEW_PASSWORD,
        },
    )

    set_cookie_headers = response.headers.get_list("set-cookie")
    assert any("access_token=" in header for header in set_cookie_headers)
    assert any("refresh_token=" in header for header in set_cookie_headers)
    assert all("HttpOnly" in header for header in set_cookie_headers)


def test_change_password_invalidates_previous_refresh_token(client, existing_user):
    """Changing the password rotates the session's tokens, which also
    revokes any other device's refresh token - only one is stored per
    user, so this is the mechanism that forces other sessions to log
    in again with the new password."""
    login_data = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    client.post(
        CHANGE_PASSWORD_URL,
        json={
            "current_password": EXISTING_USER_PASSWORD,
            "new_password": NEW_PASSWORD,
        },
    )

    # Simulate a mobile client sending the stale token in the body - the
    # cookie jar now holds the new one, which would take priority if left
    # in place, masking whether the old token was actually invalidated.
    client.cookies.clear()
    response = client.post(
        REFRESH_URL, json={"refresh_token": login_data["refresh_token"]}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


def test_change_password_does_not_affect_other_users(
    client, existing_user, other_user, db_session
):
    _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    client.post(
        CHANGE_PASSWORD_URL,
        json={
            "current_password": EXISTING_USER_PASSWORD,
            "new_password": NEW_PASSWORD,
        },
    )

    other_user_after = db_session.query(User).filter(User.id == other_user.id).first()
    assert verify_password("otheruserpassword123", other_user_after.password_hash)


def test_change_password_on_google_only_account_is_rejected(client, db_session):
    """A Google-only account has no password_hash - this must reject
    cleanly instead of crashing verify_password on None."""
    user = User(
        full_name="Google Only",
        email="googleonly-changepw@example.com",
        login_provider="google",
        google_id="google-sub-changepw-1",
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()

    token = create_access_token(user.id, user.role)
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.post(
        CHANGE_PASSWORD_URL,
        json={"current_password": "anything", "new_password": NEW_PASSWORD},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"
