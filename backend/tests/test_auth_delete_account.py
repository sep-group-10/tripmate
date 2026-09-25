"""Tests for POST /auth/delete-account."""

from app.models.user import User

LOGIN_URL = "/api/v1/auth/login"
DELETE_URL = "/api/v1/auth/delete-account"

PASSWORD = "existingpassword123"


def _login(client, email, password):
    return client.post(LOGIN_URL, json={"email": email, "password": password})


def test_delete_account_requires_authentication(client):
    response = client.post(DELETE_URL, json={"current_password": "whatever"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_delete_local_account_with_wrong_password_is_rejected(client, existing_user):
    _login(client, existing_user.email, PASSWORD)

    response = client.post(DELETE_URL, json={"current_password": "wrongpassword1"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_delete_local_account_without_password_is_rejected(client, existing_user):
    _login(client, existing_user.email, PASSWORD)

    response = client.post(DELETE_URL, json={})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_delete_local_account_succeeds(client, existing_user, db_session):
    _login(client, existing_user.email, PASSWORD)

    response = client.post(DELETE_URL, json={"current_password": PASSWORD})

    assert response.status_code == 200
    db_session.refresh(existing_user)
    assert existing_user.is_active is False
    assert existing_user.full_name == "Deleted User"
    assert (
        existing_user.email == f"deleted-{existing_user.id}@deleted-users.tripmate.com"
    )
    assert existing_user.password_hash is None


def test_delete_account_clears_cookies(client, existing_user):
    _login(client, existing_user.email, PASSWORD)

    response = client.post(DELETE_URL, json={"current_password": PASSWORD})

    set_cookie_headers = response.headers.get_list("set-cookie")
    assert any("access_token=" in header for header in set_cookie_headers)
    assert any("refresh_token=" in header for header in set_cookie_headers)


def test_deactivated_account_cannot_log_in_again(client, existing_user):
    # Captured before delete: current_user inside the endpoint is the
    # same identity-mapped object as this fixture (same session), so
    # existing_user.email would otherwise reflect the post-delete value.
    original_email = existing_user.email
    _login(client, original_email, PASSWORD)
    client.post(DELETE_URL, json={"current_password": PASSWORD})

    response = _login(client, original_email, PASSWORD)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_delete_google_account_requires_no_password(client, db_session):
    user = User(
        full_name="Google Only",
        email="googleonly-delete@example.com",
        login_provider="google",
        google_id="google-sub-delete-1",
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()

    # Google login isn't mocked here - authenticate by issuing a token
    # pair directly, matching how a real Google-login session would look.
    from app.core.security import create_access_token

    token = create_access_token(user.id, user.role)
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.post(DELETE_URL, json={})

    assert response.status_code == 200
    db_session.refresh(user)
    assert user.is_active is False
    assert user.google_id is None


def test_delete_does_not_affect_other_users(
    client, existing_user, other_user, db_session
):
    _login(client, existing_user.email, PASSWORD)

    client.post(DELETE_URL, json={"current_password": PASSWORD})

    other_after = db_session.query(User).filter(User.id == other_user.id).first()
    assert other_after.is_active is True
    assert other_after.email == other_user.email
