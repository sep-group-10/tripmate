"""Integration tests for the chat preference-processing flow."""

import uuid
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_user
from app.main import app
from app.models.conversation_history import ConversationHistory
from app.models.planning_session import PlanningSession
from app.models.trip import Trip
from app.routers import chat as chat_router
from app.schemas.agent_session import AgentSession, AgentSessionStatus
from app.schemas.preference import PreferenceResult

CHAT_URL = "/api/v1/chat"


@pytest.fixture(autouse=True)
def authenticate_chat_requests(request):
    """Use the existing auth dependency with a test user for chat requests."""
    if "client" not in request.fixturenames:
        yield
        return

    request.getfixturevalue("client")
    existing_user = request.getfixturevalue("existing_user")
    app.dependency_overrides[get_current_user] = lambda: existing_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


class FakePreferenceProcessor:
    """Record processed messages and return predefined preference results."""

    def __init__(self, results: list[PreferenceResult]):
        self.results = results
        self.calls = []

    def process(self, messages):
        self.calls.append(list(messages))
        return self.results.pop(0)


def _mock_processor(monkeypatch, *results: PreferenceResult) -> FakePreferenceProcessor:
    processor = FakePreferenceProcessor(list(results))
    monkeypatch.setattr(chat_router, "PreferenceProcessor", lambda: processor)
    return processor


class FakeChatResponseGenerator:
    """Return predefined replies and record generation inputs."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def generate(self, messages, preferences):
        self.calls.append((list(messages), preferences))
        return self.responses.pop(0)


def _mock_response_generator(monkeypatch, *responses):
    generator = FakeChatResponseGenerator(responses)
    monkeypatch.setattr(chat_router, "ChatResponseGenerator", lambda: generator)
    return generator


def _conversation(db_session, session_id):
    return (
        db_session.query(ConversationHistory)
        .filter(ConversationHistory.planning_session_id == session_id)
        .order_by(ConversationHistory.created_at.asc())
        .all()
    )


def _complete_preferences() -> PreferenceResult:
    return PreferenceResult(
        intent="trip_planning",
        destination="Kandy",
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 3),
        duration_days=3,
        budget=Decimal("50000.00"),
        travelers=2,
        interests=["culture"],
        transport_type="train",
        missing_fields=[],
    )


def _schedule_result(name="Temple", route_optimization=None):
    day = {
        "day_number": 1,
        "date": "2026-10-01",
        "day_type": "day_trip",
        "items": [
            {
                "candidate_id": "place-1",
                "category": "attraction",
                "name": name,
                "start_time": "09:00",
                "end_time": "10:30",
                "latitude": 7.2906,
                "longitude": 80.6337,
                "duration_minutes": 90,
                "opening_hours": None,
            }
        ],
        "hotel_id": None,
        "hotel_location": None,
        "warnings": [],
    }
    if route_optimization is not None:
        day["route_optimization"] = route_optimization
    return {
        "status": "ok",
        "days": [day],
        "hotel_by_destination": {},
        "unscheduled": [],
        "warnings": [],
    }


def test_start_chat_processes_normal_conversation_and_stores_messages(
    client, db_session, monkeypatch
):
    processor = _mock_processor(
        monkeypatch,
        PreferenceResult(intent="normal_conversation"),
    )
    response_generator = _mock_response_generator(
        monkeypatch, "Hello! I'd be happy to help with your travel questions."
    )
    factory_calls = []
    graph_calls = []
    monkeypatch.setattr(
        chat_router,
        "create_agent_session",
        lambda preferences: factory_calls.append(preferences),
    )
    monkeypatch.setattr(
        chat_router,
        "planning_graph",
        type("Graph", (), {"invoke": lambda self, state: graph_calls.append(state)})(),
    )

    response = client.post(
        CHAT_URL,
        json={"message": "Hello there"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    expected_reply = "Hello! I'd be happy to help with your travel questions."
    assert body["data"]["assistant_message"] == expected_reply
    assert body["data"]["itinerary"] is None

    session = body["data"]["session"]

    assert session["status"] == "pending"
    assert session["iteration_count"] == 0
    assert session["progress_message"] is None
    assert session["progress_percentage"] == 0
    assert [message.content for message in processor.calls[0]] == ["Hello there"]
    assert factory_calls == []
    assert graph_calls == []
    assert len(response_generator.calls) == 1
    assert response_generator.calls[0][1].intent == "normal_conversation"
    assert db_session.query(Trip).count() == 0
    assert [
        (entry.role, entry.message)
        for entry in _conversation(db_session, session["id"])
    ] == [
        ("user", "Hello there"),
        ("assistant", expected_reply),
    ]


def test_preferences_missing_required_trip_values_do_not_create_trip(
    client, db_session, monkeypatch
):
    _mock_response_generator(
        monkeypatch, "What dates, trip length, and budget work for you?"
    )
    _mock_processor(
        monkeypatch,
        PreferenceResult(
            intent="trip_planning",
            destination="Kandy",
            travelers=2,
            interests=["culture"],
            transport_type="train",
            missing_fields=["dates", "duration_days", "budget"],
        ),
    )

    response = client.post(CHAT_URL, json={"message": "Plan a trip to Kandy."})

    assert response.status_code == 200
    expected_reply = "What dates, trip length, and budget work for you?"
    assert response.json()["data"]["assistant_message"] == expected_reply
    assert response.json()["data"]["itinerary"] is None
    assert db_session.query(Trip).count() == 0
    assert [
        entry.message
        for entry in _conversation(db_session, response.json()["data"]["session"]["id"])
        if entry.role == "assistant"
    ] == [expected_reply]


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


def test_send_message_asks_only_for_missing_trip_fields(
    client, db_session, existing_user, monkeypatch
):
    session = _planning_session(db_session, existing_user)
    _mock_processor(
        monkeypatch,
        PreferenceResult(
            intent="trip_planning",
            destination="Kandy",
            missing_fields=["dates", "budget", "transport_type"],
        ),
    )
    response_generator = _mock_response_generator(
        monkeypatch,
        "When would you like to go, what is your budget, and how will you travel?",
    )
    factory_calls = []
    graph_calls = []
    monkeypatch.setattr(
        chat_router,
        "create_agent_session",
        lambda preferences: factory_calls.append(preferences),
    )
    monkeypatch.setattr(
        chat_router,
        "planning_graph",
        type("Graph", (), {"invoke": lambda self, state: graph_calls.append(state)})(),
    )

    response = client.post(
        f"{CHAT_URL}/{session.id}",
        json={"message": "I want to plan a trip to Kandy"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    expected_reply = (
        "When would you like to go, what is your budget, and how will you travel?"
    )
    assert body["data"]["assistant_message"] == expected_reply
    assert body["data"]["itinerary"] is None
    assert response_generator.calls[0][1].missing_fields == [
        "dates",
        "budget",
        "transport_type",
    ]
    assert body["data"]["session"] == {
        "id": str(session.id),
        "status": "pending",
        "iteration_count": 0,
        "progress_message": None,
        "progress_percentage": 0,
    }
    assert factory_calls == []
    assert graph_calls == []
    assert db_session.query(Trip).count() == 1
    assert [
        (entry.role, entry.message) for entry in _conversation(db_session, session.id)
    ] == [
        ("user", "I want to plan a trip to Kandy"),
        (
            "assistant",
            expected_reply,
        ),
    ]


def test_send_message_processes_complete_multi_turn_conversation(
    client, db_session, existing_user, monkeypatch
):
    session = _planning_session(db_session, existing_user)
    _mock_response_generator(
        monkeypatch,
        "When would you like to travel, and how many people prefer which transport?",
        "What budget do you have in mind?",
    )
    processor = _mock_processor(
        monkeypatch,
        PreferenceResult(
            intent="trip_planning",
            destination="Kandy",
            missing_fields=["dates", "travelers", "transport_type"],
        ),
        PreferenceResult(
            intent="trip_planning",
            destination="Kandy",
            travelers=2,
            transport_type="train",
            missing_fields=["budget"],
        ),
    )

    first_response = client.post(
        f"{CHAT_URL}/{session.id}",
        json={"message": "I want to visit Kandy."},
    )
    second_response = client.post(
        f"{CHAT_URL}/{session.id}",
        json={"message": "December 10-12, two people. I prefer the train."},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert [(message.type, message.content) for message in processor.calls[1]] == [
        ("human", "I want to visit Kandy."),
        (
            "ai",
            "When would you like to travel, and how many people prefer which transport?",
        ),
        ("human", "December 10-12, two people. I prefer the train."),
    ]


def test_complete_preferences_start_planning_and_persist_final_result(
    client, db_session, existing_user, monkeypatch
):
    preferences = _complete_preferences()
    existing_user.preferred_travel_style = "cultural"
    existing_user.preferred_accommodation = "hotel"
    db_session.flush()
    _mock_processor(monkeypatch, preferences)
    agent_session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy"},
    )
    final_agent_session = agent_session.model_copy(
        update={
            "status": AgentSessionStatus.COMPLETED,
            "iteration_count": 2,
            "itinerary": {"days": []},
            "tool_results": [
                {
                    "tool": "scheduling_engine",
                    "result": _schedule_result("Old schedule"),
                },
                {
                    "tool": "route_optimizer",
                    "result": _schedule_result(
                        "Optimized temple",
                        {"reordered": True, "warning": None, "local_distance_km": 2.5},
                    ),
                },
            ],
        }
    )
    factory_calls = []
    graph_calls = []

    def fake_factory(result):
        factory_calls.append(result)
        return agent_session

    class FakeGraph:
        def invoke(self, state):
            graph_calls.append(state)
            trip = db_session.query(Trip).one()
            linked_session = (
                db_session.query(PlanningSession).filter_by(trip_id=trip.id).one()
            )
            assert linked_session.trip_id == trip.id
            return {"session": final_agent_session}

    generated_reply = "Here is your Kandy itinerary for October 1 through 3."
    final_response_sessions = []

    class FakeFinalResponseGenerator:
        def generate(self, session):
            final_response_sessions.append(session)
            return generated_reply

    monkeypatch.setattr(
        chat_router, "FinalResponseGenerator", FakeFinalResponseGenerator
    )
    monkeypatch.setattr(chat_router, "create_agent_session", fake_factory)
    monkeypatch.setattr(chat_router, "planning_graph", FakeGraph())

    response = client.post(
        CHAT_URL,
        json={"message": "Plan a three-day Kandy trip for two people."},
    )

    assert response.status_code == 200
    session_id = uuid.UUID(response.json()["data"]["session"]["id"])
    session = db_session.get(PlanningSession, session_id)
    assert response.json()["data"]["assistant_message"] == generated_reply
    assert final_response_sessions == [final_agent_session]
    itinerary = response.json()["data"]["itinerary"]
    assert itinerary["status"] == "ok"
    assert itinerary["days"][0]["items"][0]["name"] == "Optimized temple"
    assert itinerary["days"][0]["route_optimization"] == {
        "reordered": True,
        "warning": None,
        "local_distance_km": 2.5,
    }
    assert factory_calls == [preferences]
    assert len(graph_calls) == 1
    assert graph_calls[0]["session"] is agent_session
    assert graph_calls[0]["planner_decision"] is None
    assert graph_calls[0]["critic_decision"] is None
    assert graph_calls[0]["last_failure"] is None
    assert graph_calls[0]["consecutive_failures"] == 0
    trips = db_session.query(Trip).all()
    assert len(trips) == 1
    trip = trips[0]
    assert trip.user_id == existing_user.id
    assert trip.travel_start_date == date(2026, 10, 1)
    assert trip.travel_end_date == date(2026, 10, 3)
    assert trip.duration == 3
    assert trip.budget == Decimal("50000.00")
    assert trip.travel_style == "cultural"
    assert trip.accommodation_preference == "hotel"
    assert session.trip_id == trip.id
    assert session.working_memory == {
        "trip_preferences": {
            "intent": "trip_planning",
            "destination": "Kandy",
            "start_date": "2026-10-01",
            "end_date": "2026-10-03",
            "duration_days": 3,
            "budget": "50000.00",
            "travelers": 2,
            "interests": ["culture"],
            "transport_type": "train",
            "missing_fields": [],
        }
    }
    assert session.status == AgentSessionStatus.COMPLETED.value
    assert session.iteration_count == 2
    assert [
        (entry.role, entry.message) for entry in _conversation(db_session, session_id)
    ] == [
        ("user", "Plan a three-day Kandy trip for two people."),
        ("assistant", generated_reply),
    ]


def test_chat_itinerary_selects_route_optimizer_or_schedule_fallback():
    schedule = _schedule_result("Scheduled place")
    optimized = _schedule_result(
        "Optimized place",
        {"reordered": True, "warning": None, "local_distance_km": 1.25},
    )
    session = AgentSession(
        goal="Plan a trip",
        tool_results=[
            {"tool": "scheduling_engine", "result": schedule},
            {"tool": "route_optimizer", "result": optimized},
            # Selection is by preferred tool type, even if a later scheduler
            # result is present in the history.
            {"tool": "scheduling_engine", "result": _schedule_result("Later schedule")},
        ],
    )

    selected = chat_router._itinerary_for_agent_session(session)
    fallback = chat_router._itinerary_for_agent_session(
        AgentSession(
            goal="Plan a trip",
            tool_results=[{"tool": "scheduling_engine", "result": schedule}],
        )
    )

    assert selected is not None
    assert selected.days[0].items[0].name == "Optimized place"
    assert selected.days[0].route_optimization["local_distance_km"] == 1.25
    assert fallback is not None
    assert fallback.days[0].items[0].name == "Scheduled place"
    assert fallback.days[0].route_optimization is None


def test_planning_failure_uses_global_safe_error_handling(client, monkeypatch):
    _mock_processor(monkeypatch, _complete_preferences())
    monkeypatch.setattr(
        chat_router,
        "create_agent_session",
        lambda preferences: AgentSession(goal="Plan a trip"),
    )

    class FailingGraph:
        def invoke(self, state):
            raise RuntimeError("planning provider secret failure")

    monkeypatch.setattr(chat_router, "planning_graph", FailingGraph())

    with TestClient(app, raise_server_exceptions=False) as safe_client:
        response = safe_client.post(
            CHAT_URL,
            json={"message": "Plan a three-day Kandy trip for two people."},
        )

    assert response.status_code == 500
    assert response.json() == {
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
        },
    }
    assert "Your trip preferences are ready for planning." not in response.text


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
