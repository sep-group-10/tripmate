"""Tests for the /admin dashboard endpoints."""

from datetime import date

from app.models.feedback import Feedback
from app.models.trip import Trip

LOGIN_URL = "/api/v1/auth/login"
STATS_URL = "/api/v1/admin/stats"
TRIPS_GROWTH_URL = "/api/v1/admin/trips-growth"
USERS_URL = "/api/v1/admin/users"
FEEDBACK_URL = "/api/v1/admin/feedback"
ACTIVITY_URL = "/api/v1/admin/activity"


def _login(client, email, password):
    response = client.post(LOGIN_URL, json={"email": email, "password": password})
    return response.json()["data"]["access_token"]


def test_stats_requires_authentication(client):
    response = client.get(STATS_URL)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_stats_blocked_for_tourist(client, existing_user):
    token = _login(client, existing_user.email, "existingpassword123")
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get(STATS_URL)

    assert response.status_code == 403


def test_stats_counts_reflect_real_rows(admin_client, db_session, existing_user):
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
    pending_feedback = Feedback(user_id=existing_user.id, rating=4, status="pending")
    resolved_feedback = Feedback(user_id=existing_user.id, rating=5, status="resolved")
    db_session.add_all([trip, pending_feedback, resolved_feedback])
    db_session.commit()

    response = admin_client.get(STATS_URL)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["draft_trips_count"] >= 1
    assert data["pending_feedback_count"] >= 1
    assert data["total_users"] >= 1


def test_trips_growth_returns_twelve_months(admin_client):
    response = admin_client.get(TRIPS_GROWTH_URL)

    assert response.status_code == 200
    months = response.json()["data"]["months"]
    assert len(months) == 12
    assert all("label" in m and "trips" in m and "users" in m for m in months)


def test_users_list_blocked_for_tourist(client, existing_user):
    token = _login(client, existing_user.email, "existingpassword123")
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get(USERS_URL)

    assert response.status_code == 403


def test_users_list_returns_paginated_users(admin_client, existing_user):
    response = admin_client.get(USERS_URL, params={"page": 1, "limit": 20})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] >= 1
    emails = [item["email"] for item in data["items"]]
    assert existing_user.email in emails
    assert all("password_hash" not in item for item in data["items"])


def test_users_list_filters_by_search(admin_client, existing_user, other_user):
    response = admin_client.get(USERS_URL, params={"q": "Existing User"})

    assert response.status_code == 200
    emails = [item["email"] for item in response.json()["data"]["items"]]
    assert existing_user.email in emails
    assert other_user.email not in emails


def test_feedback_list_includes_user_name(admin_client, db_session, existing_user):
    feedback = Feedback(
        user_id=existing_user.id,
        rating=5,
        comment="Great trip",
        status="pending",
    )
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)

    response = admin_client.get(FEEDBACK_URL)

    assert response.status_code == 200
    items = response.json()["data"]
    match = next(item for item in items if item["id"] == str(feedback.id))
    assert match["user_name"] == existing_user.full_name
    assert match["status"] == "pending"


def test_resolve_feedback_sets_outcome_and_resolver(
    admin_client, db_session, existing_user
):
    feedback = Feedback(user_id=existing_user.id, rating=3, status="pending")
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)

    response = admin_client.patch(
        f"{FEEDBACK_URL}/{feedback.id}/resolve",
        json={"outcome": "Fixed the data", "note": "Updated opening hours."},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "resolved"
    assert data["resolution_outcome"] == "Fixed the data"
    assert data["resolution_note"] == "Updated opening hours."
    assert data["resolved_by_name"] == "Tourism Test Admin"
    assert data["resolved_at"] is not None


def test_resolve_feedback_rejects_unknown_outcome(
    admin_client, db_session, existing_user
):
    feedback = Feedback(user_id=existing_user.id, rating=3, status="pending")
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)

    response = admin_client.patch(
        f"{FEEDBACK_URL}/{feedback.id}/resolve",
        json={"outcome": "Not a real outcome"},
    )

    assert response.status_code == 400


def test_resolve_feedback_missing_id_returns_404(admin_client):
    response = admin_client.patch(
        f"{FEEDBACK_URL}/00000000-0000-0000-0000-000000000000/resolve",
        json={"outcome": "Fixed the data"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_reopen_feedback_clears_resolution(admin_client, db_session, existing_user):
    feedback = Feedback(
        user_id=existing_user.id,
        rating=3,
        status="resolved",
        resolution_outcome="Fixed the data",
        resolution_note="Some note",
    )
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)

    response = admin_client.patch(f"{FEEDBACK_URL}/{feedback.id}/reopen")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "pending"
    assert data["resolution_outcome"] is None
    assert data["resolution_note"] is None
    assert data["resolved_at"] is None


def test_delete_feedback_blocked_for_plain_admin(
    admin_client, db_session, existing_user
):
    feedback = Feedback(user_id=existing_user.id, rating=2, status="pending")
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)

    response = admin_client.delete(f"{FEEDBACK_URL}/{feedback.id}")

    assert response.status_code == 403


def test_superadmin_can_delete_feedback(superadmin_client, db_session, existing_user):
    feedback = Feedback(user_id=existing_user.id, rating=2, status="pending")
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)
    feedback_id = feedback.id

    response = superadmin_client.delete(f"{FEEDBACK_URL}/{feedback_id}")

    assert response.status_code == 200
    assert db_session.query(Feedback).filter(Feedback.id == feedback_id).first() is None


def test_delete_feedback_missing_id_returns_404(superadmin_client):
    response = superadmin_client.delete(
        f"{FEEDBACK_URL}/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_activity_requires_authentication(client):
    response = client.get(ACTIVITY_URL)

    assert response.status_code == 401


def test_activity_blocked_for_tourist(client, existing_user):
    token = _login(client, existing_user.email, "existingpassword123")
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get(ACTIVITY_URL)

    assert response.status_code == 403


def test_activity_logs_destination_create(admin_client):
    create_response = admin_client.post(
        "/api/v1/destinations",
        json={
            "name": "Activity Log Test Destination",
            "country": "Sri Lanka",
            "region": "Test Region",
            "latitude": 7.0,
            "longitude": 80.0,
        },
    )
    assert create_response.status_code == 201

    response = admin_client.get(ACTIVITY_URL)

    assert response.status_code == 200
    entries = response.json()["data"]
    assert any(
        entry["kind"] == "Destination"
        and "Activity Log Test Destination added" == entry["title"]
        for entry in entries
    )


def test_activity_logs_feedback_resolution(admin_client, db_session, existing_user):
    feedback = Feedback(user_id=existing_user.id, rating=4, status="pending")
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)

    patch_response = admin_client.patch(
        f"{FEEDBACK_URL}/{feedback.id}/resolve", json={"outcome": "Fixed the data"}
    )
    assert patch_response.status_code == 200

    response = admin_client.get(ACTIVITY_URL)

    assert response.status_code == 200
    entries = response.json()["data"]
    assert any(
        entry["kind"] == "Feedback" and "resolved" in entry["title"]
        for entry in entries
    )


def test_activity_respects_limit(admin_client):
    for i in range(3):
        admin_client.post(
            "/api/v1/destinations",
            json={
                "name": f"Limit Test Destination {i}",
                "country": "Sri Lanka",
                "latitude": 7.0,
                "longitude": 80.0,
            },
        )

    response = admin_client.get(ACTIVITY_URL, params={"limit": 2})

    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
