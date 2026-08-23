"""Tests for GET/PUT /users/me: fetching and updating a user's own
profile, and confirming users can't affect or read each other's data."""

from app.models.user import User

LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/users/me"

EXISTING_USER_PASSWORD = "existingpassword123"
OTHER_USER_PASSWORD = "otheruserpassword123"


def _login(client, email, password):
    """Log in and return just the access token, for tests that only
    need an authenticated client."""
    response = client.post(LOGIN_URL, json={"email": email, "password": password})
    return response.json()["data"]["access_token"]


def test_get_my_profile_returns_own_data(client, existing_user):
    token = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == str(existing_user.id)
    assert data["email"] == existing_user.email
    assert data["full_name"] == existing_user.full_name


def test_get_my_profile_never_returns_password_fields(client, existing_user):
    token = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    data = response.json()["data"]
    assert "password" not in data
    assert "password_hash" not in data


def test_get_my_profile_without_token_returns_401(client):
    response = client.get(ME_URL)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_get_my_profile_returns_the_correct_user_among_many(
    client, existing_user, other_user
):
    existing_token = _login(client, existing_user.email, EXISTING_USER_PASSWORD)
    other_token = _login(client, other_user.email, OTHER_USER_PASSWORD)

    existing_response = client.get(
        ME_URL, headers={"Authorization": f"Bearer {existing_token}"}
    )
    other_response = client.get(
        ME_URL, headers={"Authorization": f"Bearer {other_token}"}
    )

    assert existing_response.json()["data"]["id"] == str(existing_user.id)
    assert other_response.json()["data"]["id"] == str(other_user.id)
    assert existing_response.json()["data"]["id"] != other_response.json()["data"]["id"]


def test_update_my_profile_persists_changes(client, existing_user):
    token = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.put(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Updated Name",
            "preferred_travel_style": "adventure",
            "preferred_accommodation": "hostel",
            "typical_budget_range": "budget",
            "interests": ["hiking", "food"],
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["full_name"] == "Updated Name"
    assert data["preferred_travel_style"] == "adventure"
    assert data["preferred_accommodation"] == "hostel"
    assert data["typical_budget_range"] == "budget"
    assert data["interests"] == ["hiking", "food"]


def test_update_my_profile_changes_are_visible_on_subsequent_get(client, existing_user):
    token = _login(client, existing_user.email, EXISTING_USER_PASSWORD)
    client.put(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={"preferred_travel_style": "luxury"},
    )

    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.json()["data"]["preferred_travel_style"] == "luxury"


def test_update_my_profile_partial_update_does_not_clobber_other_fields(
    client, existing_user
):
    token = _login(client, existing_user.email, EXISTING_USER_PASSWORD)
    client.put(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={"preferred_travel_style": "adventure", "interests": ["hiking"]},
    )

    response = client.put(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={"typical_budget_range": "mid-range"},
    )

    data = response.json()["data"]
    assert data["preferred_travel_style"] == "adventure"
    assert data["interests"] == ["hiking"]
    assert data["typical_budget_range"] == "mid-range"


def test_update_my_profile_rejects_role_change(client, existing_user, db_session):
    token = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.put(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={"role": "SUPER_ADMIN"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    user = db_session.query(User).filter(User.id == existing_user.id).first()
    assert user.role == "TOURIST"


def test_update_my_profile_rejects_email_change(client, existing_user, db_session):
    token = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.put(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "hacked@example.com"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    user = db_session.query(User).filter(User.id == existing_user.id).first()
    assert user.email == existing_user.email


def test_update_my_profile_rejects_is_active_change(client, existing_user, db_session):
    token = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.put(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={"is_active": False},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_update_my_profile_without_token_returns_401(client):
    response = client.put(ME_URL, json={"full_name": "Should Not Work"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_update_my_profile_blank_full_name_returns_validation_error(
    client, existing_user
):
    token = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    response = client.put(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "   "},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_update_my_profile_only_affects_own_account_not_others(
    client, existing_user, other_user, db_session
):
    existing_token = _login(client, existing_user.email, EXISTING_USER_PASSWORD)

    client.put(
        ME_URL,
        headers={"Authorization": f"Bearer {existing_token}"},
        json={"full_name": "Only Mine Should Change"},
    )

    other_user_after = db_session.query(User).filter(User.id == other_user.id).first()
    assert other_user_after.full_name == "Other User"
