"""Tests for POST /auth/register: valid registration, duplicate email,
and invalid input handling. Registration also logs the user in
immediately (same token issuance as /login), so the response shape
matches LoginData: {access_token, user}."""

from app.core.security import ACCESS_TOKEN_COOKIE_NAME
from app.models.user import User

REGISTER_URL = "/api/v1/auth/register"

VALID_PAYLOAD = {
    "full_name": "Kaja Theepan",
    "email": "kaja@example.com",
    "password": "supersecret123",
}


def test_register_success_returns_created_user(client, db_session):
    response = client.post(REGISTER_URL, json=VALID_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert "access_token" in data

    user = data["user"]
    assert user["email"] == VALID_PAYLOAD["email"]
    assert user["full_name"] == VALID_PAYLOAD["full_name"]
    assert user["role"] == "TOURIST"
    assert user["is_active"] is True
    assert user["is_email_verified"] is False
    assert "id" in user
    assert "created_at" in user
    assert user["created_at"].endswith("Z")


def test_register_success_sets_httponly_cookie(client):
    response = client.post(REGISTER_URL, json=VALID_PAYLOAD)

    set_cookie = response.headers.get("set-cookie")
    assert set_cookie is not None
    assert ACCESS_TOKEN_COOKIE_NAME in set_cookie
    assert "HttpOnly" in set_cookie


def test_register_never_returns_password_fields(client):
    response = client.post(REGISTER_URL, json=VALID_PAYLOAD)

    user = response.json()["data"]["user"]
    assert "password" not in user
    assert "password_hash" not in user


def test_register_persists_hashed_password_not_plaintext(client, db_session):
    client.post(REGISTER_URL, json=VALID_PAYLOAD)

    user = db_session.query(User).filter(User.email == VALID_PAYLOAD["email"]).first()
    assert user is not None
    assert user.password_hash != VALID_PAYLOAD["password"]
    assert user.password_hash.startswith("$2b$")


def test_register_duplicate_email_returns_conflict(client, existing_user):
    payload = {**VALID_PAYLOAD, "email": existing_user.email}

    response = client.post(REGISTER_URL, json=payload)

    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_register_duplicate_email_different_case_returns_conflict(
    client, existing_user
):
    payload = {**VALID_PAYLOAD, "email": existing_user.email.upper()}

    response = client.post(REGISTER_URL, json=payload)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_register_stores_email_normalized_to_lowercase(client, db_session):
    payload = {**VALID_PAYLOAD, "email": "MixedCase@Example.com"}

    response = client.post(REGISTER_URL, json=payload)

    assert response.status_code == 201
    assert response.json()["data"]["user"]["email"] == "mixedcase@example.com"
    user = db_session.query(User).filter(User.email == "mixedcase@example.com").first()
    assert user is not None


def test_register_duplicate_email_does_not_create_second_row(
    client, existing_user, db_session
):
    payload = {**VALID_PAYLOAD, "email": existing_user.email}

    client.post(REGISTER_URL, json=payload)

    count = db_session.query(User).filter(User.email == existing_user.email).count()
    assert count == 1


def test_register_invalid_email_format_returns_validation_error(client):
    payload = {**VALID_PAYLOAD, "email": "not-an-email"}

    response = client.post(REGISTER_URL, json=payload)

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    fields = {detail["field"] for detail in body["error"]["details"]}
    assert "email" in fields


def test_register_short_password_returns_validation_error(client):
    payload = {**VALID_PAYLOAD, "email": "shortpw@example.com", "password": "short"}

    response = client.post(REGISTER_URL, json=payload)

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    fields = {detail["field"] for detail in body["error"]["details"]}
    assert "password" in fields


def test_register_whitespace_only_password_returns_validation_error(client):
    payload = {
        **VALID_PAYLOAD,
        "email": "whitespace@example.com",
        "password": "        ",
    }

    response = client.post(REGISTER_URL, json=payload)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_register_whitespace_only_name_returns_validation_error(client):
    payload = {**VALID_PAYLOAD, "email": "blankname@example.com", "full_name": "   "}

    response = client.post(REGISTER_URL, json=payload)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_register_missing_fields_returns_validation_error(client):
    response = client.post(REGISTER_URL, json={"email": "missing@example.com"})

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    fields = {detail["field"] for detail in body["error"]["details"]}
    assert "full_name" in fields
    assert "password" in fields


def test_register_rejects_invalid_json_types(client):
    payload = {**VALID_PAYLOAD, "email": "typecheck@example.com", "password": 12345678}

    response = client.post(REGISTER_URL, json=payload)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_register_does_not_leak_stack_trace_details(client):
    payload = {**VALID_PAYLOAD, "email": "not-an-email"}

    response = client.post(REGISTER_URL, json=payload)

    body_text = response.text
    assert "Traceback" not in body_text
    assert 'File "' not in body_text
