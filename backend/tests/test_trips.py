from datetime import date, datetime, time, timezone
from decimal import Decimal

from app.models.conversation_history import ConversationHistory
from app.models.itinerary import Itinerary
from app.models.itinerary_day import ItineraryDay
from app.models.itinerary_day_item import ItineraryDayItem
from app.models.planning_session import PlanningSession
from app.models.trip import Trip

LOGIN_URL = "/api/v1/auth/login"
TRIPS_URL = "/api/v1/trips"


def _add_itinerary(db_session, trip, *, title="Temple visit", created_at=None):
    itinerary = Itinerary(
        trip_id=trip.id,
        total_estimated_cost=Decimal("12500.00"),
        route_info={"mode": "walking"},
        weather_info={"forecast": "sunny"},
    )
    if created_at is not None:
        itinerary.created_at = created_at
    db_session.add(itinerary)
    db_session.flush()
    day = ItineraryDay(
        itinerary_id=itinerary.id,
        day_number=1,
        date=date(2026, 11, 1),
        title="Cultural day",
        summary="Explore the city",
    )
    db_session.add(day)
    db_session.flush()
    db_session.add(
        ItineraryDayItem(
            itinerary_day_id=day.id,
            item_type="attraction",
            title=title,
            description="Morning visit",
            start_time=time(9, 0),
            end_time=time(10, 30),
            location="Kandy",
            estimated_cost=Decimal("1000.00"),
            sort_order=0,
        )
    )
    return itinerary


def test_trip_details_return_persisted_itinerary_and_items(
    client, db_session, existing_user
):
    trip = _add_trip(db_session, existing_user, status="generated")
    itinerary = _add_itinerary(db_session, trip)
    session = PlanningSession(
        user_id=existing_user.id,
        trip_id=trip.id,
        working_memory={"trip_preferences": {"destination": "Kandy"}},
        status="completed",
        iteration_count=1,
        progress_percentage=100,
    )
    db_session.add(session)
    db_session.commit()
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.get(
        f"{TRIPS_URL}/{trip.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == str(trip.id)
    assert data["destination"] == "Kandy"
    assert data["itinerary"]["id"] == str(itinerary.id)
    assert data["itinerary"]["route_info"] == {"mode": "walking"}
    assert data["itinerary"]["days"][0]["day_number"] == 1
    assert data["itinerary"]["days"][0]["items"][0]["title"] == "Temple visit"


def test_trip_details_return_newer_itinerary_for_same_trip(
    client, db_session, existing_user
):
    trip = _add_trip(db_session, existing_user, status="generated")
    _add_itinerary(
        db_session,
        trip,
        title="Earlier stop",
        created_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )
    latest = _add_itinerary(
        db_session,
        trip,
        title="Latest stop",
        created_at=datetime(2026, 9, 2, tzinfo=timezone.utc),
    )
    db_session.commit()
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.get(
        f"{TRIPS_URL}/{trip.id}", headers={"Authorization": f"Bearer {token}"}
    )

    data = response.json()["data"]
    assert response.status_code == 200
    assert data["itinerary"]["id"] == str(latest.id)
    assert data["itinerary"]["days"][0]["items"][0]["title"] == "Latest stop"


def test_trip_details_deterministically_return_newest_of_three_itineraries(
    client, db_session, existing_user
):
    trip = _add_trip(db_session, existing_user, status="generated")
    for day, title in ((1, "First stop"), (2, "Second stop")):
        _add_itinerary(
            db_session,
            trip,
            title=title,
            created_at=datetime(2026, 9, day, tzinfo=timezone.utc),
        )
    latest = _add_itinerary(
        db_session,
        trip,
        title="Third stop",
        created_at=datetime(2026, 9, 3, tzinfo=timezone.utc),
    )
    db_session.commit()
    token = _login(client, existing_user.email, "existingpassword123")
    headers = {"Authorization": f"Bearer {token}"}

    first_response = client.get(f"{TRIPS_URL}/{trip.id}", headers=headers)
    second_response = client.get(f"{TRIPS_URL}/{trip.id}", headers=headers)

    first_data = first_response.json()["data"]["itinerary"]
    second_data = second_response.json()["data"]["itinerary"]
    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_data["id"] == str(latest.id)
    assert second_data["id"] == str(latest.id)
    assert first_data["days"][0]["items"][0]["title"] == "Third stop"


def test_trip_details_are_available_for_saved_trip(client, db_session, existing_user):
    trip = _add_trip(db_session, existing_user, status="saved")
    _add_itinerary(
        db_session,
        trip,
        title="Earlier saved stop",
        created_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )
    latest = _add_itinerary(
        db_session,
        trip,
        title="Latest saved stop",
        created_at=datetime(2026, 9, 2, tzinfo=timezone.utc),
    )
    db_session.commit()
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.get(
        f"{TRIPS_URL}/{trip.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "saved"
    assert response.json()["data"]["itinerary"]["id"] == str(latest.id)
    assert (
        response.json()["data"]["itinerary"]["days"][0]["items"][0]["title"]
        == "Latest saved stop"
    )


def test_trip_details_hide_other_users_and_missing_trips(
    client, db_session, existing_user, other_user
):
    trip = _add_trip(db_session, other_user)
    token = _login(client, existing_user.email, "existingpassword123")
    headers = {"Authorization": f"Bearer {token}"}

    forbidden = client.get(f"{TRIPS_URL}/{trip.id}", headers=headers)
    missing = client.get(
        f"{TRIPS_URL}/00000000-0000-0000-0000-000000000001", headers=headers
    )

    assert forbidden.status_code == 404
    assert missing.status_code == 404


def test_draft_trip_details_work_without_an_itinerary(
    client, db_session, existing_user
):
    trip = _add_trip(db_session, existing_user, status="draft")
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.get(
        f"{TRIPS_URL}/{trip.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["data"]["itinerary"] is None


def _login(client, email, password):
    response = client.post(LOGIN_URL, json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def _add_trip(db_session, user, *, status="draft", budget=50000):
    trip = Trip(
        user_id=user.id,
        status=status,
        travel_start_date=date(2026, 11, 1),
        travel_end_date=date(2026, 11, 4),
        duration=3,
        budget=Decimal(str(budget)),
        travel_style="cultural",
        accommodation_preference="hotel",
    )
    db_session.add(trip)
    db_session.flush()
    return trip


def test_authenticated_user_can_retrieve_their_trips(client, db_session, existing_user):
    own_trip = _add_trip(db_session, existing_user, status="generated")
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.get(TRIPS_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0] == {
        "id": str(own_trip.id),
        "status": "generated",
        "title": None,
        "travel_start_date": "2026-11-01",
        "travel_end_date": "2026-11-04",
        "duration": 3,
        "budget": "50000.00",
        "travel_style": "cultural",
        "accommodation_preference": "hotel",
        "created_at": own_trip.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated_at": own_trip.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def test_trips_list_includes_only_authenticated_users_trips(
    client, db_session, existing_user, other_user
):
    own_trip = _add_trip(db_session, existing_user)
    _add_trip(db_session, other_user, status="saved", budget=90000)
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.get(TRIPS_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    trips = response.json()["data"]
    assert [trip["id"] for trip in trips] == [str(own_trip.id)]
    assert all(trip["status"] in {"draft", "generated", "saved"} for trip in trips)


def test_trips_list_returns_empty_data_when_user_has_no_trips(client, existing_user):
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.get(TRIPS_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"success": True, "data": []}


def test_trips_list_requires_authentication(client):
    response = client.get(TRIPS_URL)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_resume_returns_the_owned_draft_session_and_conversation(
    client, db_session, existing_user
):
    trip = _add_trip(db_session, existing_user, status="draft")
    session = PlanningSession(
        user_id=existing_user.id,
        trip_id=trip.id,
        status="pending",
        iteration_count=0,
        progress_message=None,
        progress_percentage=0,
    )
    db_session.add(session)
    db_session.flush()
    db_session.add_all(
        [
            ConversationHistory(
                planning_session_id=session.id,
                role="user",
                message="I want to plan a trip to Kandy.",
            ),
            ConversationHistory(
                planning_session_id=session.id,
                role="assistant",
                message="What dates would you prefer?",
            ),
        ]
    )
    db_session.commit()
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.get(
        f"{TRIPS_URL}/{trip.id}/resume",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["trip"]["id"] == str(trip.id)
    assert data["trip"]["status"] == "draft"
    assert data["session"]["id"] == str(session.id)
    assert [(entry["role"], entry["message"]) for entry in data["conversation"]] == [
        ("user", "I want to plan a trip to Kandy."),
        ("assistant", "What dates would you prefer?"),
    ]


def test_user_cannot_resume_another_users_draft(
    client, db_session, existing_user, other_user
):
    trip = _add_trip(db_session, other_user, status="draft")
    session = PlanningSession(
        user_id=other_user.id,
        trip_id=trip.id,
        status="pending",
        iteration_count=0,
        progress_message=None,
        progress_percentage=0,
    )
    db_session.add(session)
    db_session.flush()
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.get(
        f"{TRIPS_URL}/{trip.id}/resume",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_generated_trip_with_a_session_can_be_resumed(
    client, db_session, existing_user
):
    trip = _add_trip(db_session, existing_user, status="generated")
    session = PlanningSession(
        user_id=existing_user.id,
        trip_id=trip.id,
        status="completed",
        iteration_count=1,
        progress_message=None,
        progress_percentage=100,
    )
    db_session.add(session)
    db_session.flush()
    db_session.add(
        ConversationHistory(
            planning_session_id=session.id,
            role="user",
            message="Please refine the itinerary.",
        )
    )
    db_session.commit()
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.get(
        f"{TRIPS_URL}/{trip.id}/resume",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["trip"]["status"] == "generated"
    assert data["session"]["id"] == str(session.id)
    assert [message["message"] for message in data["conversation"]] == [
        "Please refine the itinerary."
    ]


def test_saved_trip_cannot_be_resumed(client, db_session, existing_user):
    trip = _add_trip(db_session, existing_user, status="saved")
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.get(
        f"{TRIPS_URL}/{trip.id}/resume",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_user_can_rename_owned_draft(client, db_session, existing_user):
    trip = _add_trip(db_session, existing_user, status="draft")
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.patch(
        f"{TRIPS_URL}/{trip.id}/title",
        json={"title": "  Hill country weekend  "},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["id"] == str(trip.id)
    assert response.json()["data"]["title"] == "Hill country weekend"
    db_session.refresh(trip)
    assert trip.title == "Hill country weekend"


def test_user_cannot_rename_another_users_draft(
    client, db_session, existing_user, other_user
):
    trip = _add_trip(db_session, other_user, status="draft")
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.patch(
        f"{TRIPS_URL}/{trip.id}/title",
        json={"title": "Not yours"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    db_session.refresh(trip)
    assert trip.title is None


def test_generated_and_saved_trips_cannot_be_renamed(client, db_session, existing_user):
    trips = [
        _add_trip(db_session, existing_user, status="generated"),
        _add_trip(db_session, existing_user, status="saved", budget=90000),
    ]
    token = _login(client, existing_user.email, "existingpassword123")
    headers = {"Authorization": f"Bearer {token}"}

    for trip in trips:
        response = client.patch(
            f"{TRIPS_URL}/{trip.id}/title",
            json={"title": "Should not change"},
            headers=headers,
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"
        db_session.refresh(trip)
        assert trip.title is None


def test_rename_rejects_empty_or_whitespace_title(client, db_session, existing_user):
    trip = _add_trip(db_session, existing_user, status="draft")
    token = _login(client, existing_user.email, "existingpassword123")
    headers = {"Authorization": f"Bearer {token}"}

    for title in ("", "   "):
        response = client.patch(
            f"{TRIPS_URL}/{trip.id}/title",
            json={"title": title},
            headers=headers,
        )
        assert response.status_code == 422


def test_user_can_discard_owned_draft_and_its_session_history(
    client, db_session, existing_user
):
    from app.models.agent_execution_trace import AgentExecutionTrace

    trip = _add_trip(db_session, existing_user, status="draft")
    session = PlanningSession(
        user_id=existing_user.id,
        trip_id=trip.id,
        status="pending",
        iteration_count=0,
        progress_message=None,
        progress_percentage=0,
    )
    db_session.add(session)
    db_session.flush()
    message = ConversationHistory(
        planning_session_id=session.id,
        role="user",
        message="Plan a trip.",
    )
    trace = AgentExecutionTrace(
        planning_session_id=session.id,
        tool_name="test_tool",
        tool_input={},
        tool_output={},
        success=True,
        iteration_number=1,
    )
    db_session.add_all([message, trace])
    db_session.commit()
    trip_id = trip.id
    session_id = session.id
    message_id = message.id
    trace_id = trace.id
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.delete(
        f"{TRIPS_URL}/{trip_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["id"] == str(trip_id)
    assert db_session.get(Trip, trip_id) is None
    assert db_session.get(PlanningSession, session_id) is None
    assert db_session.get(ConversationHistory, message_id) is None
    assert db_session.get(AgentExecutionTrace, trace_id) is None


def test_user_cannot_discard_another_users_draft(
    client, db_session, existing_user, other_user
):
    trip = _add_trip(db_session, other_user, status="draft")
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.delete(
        f"{TRIPS_URL}/{trip.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    db_session.refresh(trip)
    assert trip.status == "draft"


def test_generated_and_saved_trips_cannot_be_discarded(
    client, db_session, existing_user
):
    trips = [
        _add_trip(db_session, existing_user, status="generated"),
        _add_trip(db_session, existing_user, status="saved", budget=90000),
    ]
    token = _login(client, existing_user.email, "existingpassword123")
    headers = {"Authorization": f"Bearer {token}"}

    for trip in trips:
        response = client.delete(f"{TRIPS_URL}/{trip.id}", headers=headers)
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"
        assert db_session.get(Trip, trip.id) is not None


def test_authenticated_user_can_save_generated_trip_and_transition_to_saved(
    client, db_session, existing_user
):
    trip = _add_trip(db_session, existing_user, status="generated")
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.post(
        f"{TRIPS_URL}/{trip.id}/save",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["id"] == str(trip.id)
    assert response.json()["data"]["status"] == "saved"
    db_session.refresh(trip)
    assert trip.status == "saved"


def test_authenticated_user_can_unsave_trip_and_transition_to_generated(
    client, db_session, existing_user
):
    trip = _add_trip(db_session, existing_user, status="saved")
    token = _login(client, existing_user.email, "existingpassword123")

    response = client.delete(
        f"{TRIPS_URL}/{trip.id}/save",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["id"] == str(trip.id)
    assert response.json()["data"]["status"] == "generated"
    db_session.refresh(trip)
    assert trip.status == "generated"


def test_user_cannot_save_or_unsave_another_users_trip(
    client, db_session, existing_user, other_user
):
    generated_trip = _add_trip(db_session, other_user, status="generated")
    saved_trip = _add_trip(db_session, other_user, status="saved", budget=90000)
    token = _login(client, existing_user.email, "existingpassword123")
    headers = {"Authorization": f"Bearer {token}"}

    save_response = client.post(
        f"{TRIPS_URL}/{generated_trip.id}/save", headers=headers
    )
    unsave_response = client.delete(
        f"{TRIPS_URL}/{saved_trip.id}/save", headers=headers
    )

    assert save_response.status_code == 404
    assert unsave_response.status_code == 404
    db_session.refresh(generated_trip)
    db_session.refresh(saved_trip)
    assert generated_trip.status == "generated"
    assert saved_trip.status == "saved"


def test_invalid_trip_status_transitions_are_rejected(
    client, db_session, existing_user
):
    draft_trip = _add_trip(db_session, existing_user, status="draft")
    generated_trip = _add_trip(db_session, existing_user, status="generated")
    token = _login(client, existing_user.email, "existingpassword123")
    headers = {"Authorization": f"Bearer {token}"}

    save_response = client.post(f"{TRIPS_URL}/{draft_trip.id}/save", headers=headers)
    unsave_response = client.delete(
        f"{TRIPS_URL}/{generated_trip.id}/save", headers=headers
    )

    assert save_response.status_code == 400
    assert save_response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert unsave_response.status_code == 400
    assert unsave_response.json()["error"]["code"] == "VALIDATION_ERROR"
    db_session.refresh(draft_trip)
    db_session.refresh(generated_trip)
    assert draft_trip.status == "draft"
    assert generated_trip.status == "generated"


def test_save_and_unsave_require_authentication(client, db_session, existing_user):
    generated_trip = _add_trip(db_session, existing_user, status="generated")
    saved_trip = _add_trip(db_session, existing_user, status="saved", budget=90000)

    save_response = client.post(f"{TRIPS_URL}/{generated_trip.id}/save")
    unsave_response = client.delete(f"{TRIPS_URL}/{saved_trip.id}/save")

    assert save_response.status_code == 401
    assert save_response.json()["error"]["code"] == "UNAUTHORIZED"
    assert unsave_response.status_code == 401
    assert unsave_response.json()["error"]["code"] == "UNAUTHORIZED"
