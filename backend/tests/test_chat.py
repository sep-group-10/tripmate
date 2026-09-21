"""API tests for POST /chat/{session_id}."""

import uuid
from datetime import date
from decimal import Decimal

from app.models.planning_session import PlanningSession
from app.models.trip import Trip

CHAT_URL = "/api/v1/chat"


def test_start_chat_creates_planning_session(client):
    response = client.post(
        CHAT_URL,
        json={"message": "I want to plan a trip to Kandy"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["assistant_message"] == "Thanks! I received your message."

    session = body["data"]["session"]

    assert session["status"] == "pending"
    assert session["iteration_count"] == 0
    assert session["progress_message"] is None
    assert session["progress_percentage"] == 0


def _planning_session(db_session, user) -> PlanningSession:
    """Create the minimum trip and planning session required for chat tests."""
    trip = Trip(
        user_id=user.id,
        status="draft",
        travel_start_date=date(2026, 10, 1),
        travel_end_date=date(2026, 10, 3),
        duration=3,
        budget=Decimal("500.00"),
        travel_style="cultural",
        accommodation_preference="hotel",
    )
    db_session.add(trip)
    db_session.flush()

    session = PlanningSession(
        trip_id=trip.id,
        status="pending",
        iteration_count=0,
        progress_message=None,
        progress_percentage=0,
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


def test_send_message_to_existing_planning_session(client, db_session, existing_user):
    session = _planning_session(db_session, existing_user)

    response = client.post(
        f"{CHAT_URL}/{session.id}",
        json={"message": "I want to plan a trip to Kandy"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["assistant_message"] == "Thanks! I received your message."
    assert body["data"]["session"] == {
        "id": str(session.id),
        "status": "pending",
        "iteration_count": 0,
        "progress_message": None,
        "progress_percentage": 0,
    }


def test_send_message_to_missing_planning_session_returns_404(client):
    response = client.post(
        f"{CHAT_URL}/{uuid.uuid4()}",
        json={"message": "I want to plan a trip to Kandy"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert response.json()["error"]["message"] == "Planning session not found"


def test_send_message_without_message_returns_validation_error(client):
    response = client.post(f"{CHAT_URL}/{uuid.uuid4()}", json={})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_send_blank_message_returns_validation_error(client):
    response = client.post(f"{CHAT_URL}/{uuid.uuid4()}", json={"message": "   "})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
