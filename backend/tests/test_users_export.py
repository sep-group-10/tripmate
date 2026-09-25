"""Tests for GET /users/me/export."""

from datetime import date

from app.models.feedback import Feedback
from app.models.trip import Trip

LOGIN_URL = "/api/v1/auth/login"
EXPORT_URL = "/api/v1/users/me/export"

PASSWORD = "existingpassword123"


def _login(client, email, password):
    response = client.post(LOGIN_URL, json={"email": email, "password": password})
    return response.json()["data"]["access_token"]


def test_export_requires_authentication(client):
    response = client.get(EXPORT_URL)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_export_returns_own_profile(client, existing_user):
    token = _login(client, existing_user.email, PASSWORD)
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get(EXPORT_URL)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["profile"]["email"] == existing_user.email
    assert data["profile"]["id"] == str(existing_user.id)
    assert "password_hash" not in data["profile"]


def test_export_includes_own_trips_and_feedback(client, existing_user, db_session):
    trip = Trip(
        user_id=existing_user.id,
        status="draft",
        travel_start_date=date(2026, 1, 1),
        travel_end_date=date(2026, 1, 5),
        duration=4,
        budget=500,
        travel_style="Relaxed",
        accommodation_preference="Hotel",
    )
    feedback = Feedback(
        user_id=existing_user.id,
        rating=5,
        comment="Loved it",
    )
    db_session.add_all([trip, feedback])
    db_session.commit()

    token = _login(client, existing_user.email, PASSWORD)
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get(EXPORT_URL)

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["trips"]) == 1
    assert data["trips"][0]["travel_style"] == "Relaxed"
    assert len(data["feedback"]) == 1
    assert data["feedback"][0]["comment"] == "Loved it"


def test_export_does_not_include_other_users_data(
    client, existing_user, other_user, db_session
):
    other_trip = Trip(
        user_id=other_user.id,
        status="draft",
        travel_start_date=date(2026, 1, 1),
        travel_end_date=date(2026, 1, 5),
        duration=4,
        budget=500,
        travel_style="Packed",
        accommodation_preference="Hostel",
    )
    db_session.add(other_trip)
    db_session.commit()

    token = _login(client, existing_user.email, PASSWORD)
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get(EXPORT_URL)

    assert response.status_code == 200
    assert response.json()["data"]["trips"] == []


def test_export_with_no_trips_or_feedback_returns_empty_lists(client, existing_user):
    token = _login(client, existing_user.email, PASSWORD)
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get(EXPORT_URL)

    data = response.json()["data"]
    assert data["trips"] == []
    assert data["feedback"] == []
