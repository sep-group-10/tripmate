"""Integration tests for the chat preference-processing flow."""

import uuid
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.conversation_history import ConversationHistory
from app.models.planning_session import PlanningSession
from app.models.trip import Trip
from app.routers import chat as chat_router
from app.schemas.agent_session import AgentSession, AgentSessionStatus
from app.schemas.preference import PreferenceResult

CHAT_URL = "/api/v1/chat"


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
        duration_days=3,
        budget=Decimal("50000.00"),
        travelers=2,
        interests=["culture"],
        transport_type="train",
        missing_fields=[],
    )


def test_start_chat_processes_normal_conversation_and_stores_messages(
    client, db_session, monkeypatch
):
    processor = _mock_processor(
        monkeypatch,
        PreferenceResult(intent="normal_conversation"),
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
    assert body["data"]["assistant_message"] == "Hello! How can I help you today?"

    session = body["data"]["session"]

    assert session["status"] == "pending"
    assert session["iteration_count"] == 0
    assert session["progress_message"] is None
    assert session["progress_percentage"] == 0
    assert [message.content for message in processor.calls[0]] == ["Hello there"]
    assert factory_calls == []
    assert graph_calls == []
    assert [
        (entry.role, entry.message)
        for entry in _conversation(db_session, session["id"])
    ] == [
        ("user", "Hello there"),
        ("assistant", "Hello! How can I help you today?"),
    ]


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
    assert body["data"]["assistant_message"] == (
        "When are you planning to travel? What is your budget for the trip? Which transport type do you prefer?"
    )
    assert body["data"]["session"] == {
        "id": str(session.id),
        "status": "pending",
        "iteration_count": 0,
        "progress_message": None,
        "progress_percentage": 0,
    }
    assert factory_calls == []
    assert graph_calls == []
    assert [
        (entry.role, entry.message) for entry in _conversation(db_session, session.id)
    ] == [
        ("user", "I want to plan a trip to Kandy"),
        (
            "assistant",
            "When are you planning to travel? What is your budget for the trip? "
            "Which transport type do you prefer?",
        ),
    ]


def test_send_message_processes_complete_multi_turn_conversation(
    client, db_session, existing_user, monkeypatch
):
    session = _planning_session(db_session, existing_user)
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
            "When are you planning to travel? How many people will be traveling? "
            "Which transport type do you prefer?",
        ),
        ("human", "December 10-12, two people. I prefer the train."),
    ]


def test_complete_preferences_start_planning_and_persist_final_result(
    client, db_session, monkeypatch
):
    preferences = _complete_preferences()
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
            return {"session": final_agent_session}

    monkeypatch.setattr(chat_router, "create_agent_session", fake_factory)
    monkeypatch.setattr(chat_router, "planning_graph", FakeGraph())

    response = client.post(
        CHAT_URL,
        json={"message": "Plan a three-day Kandy trip for two people."},
    )

    assert response.status_code == 200
    session_id = uuid.UUID(response.json()["data"]["session"]["id"])
    session = db_session.get(PlanningSession, session_id)
    assert (
        response.json()["data"]["assistant_message"]
        == "Your trip itinerary has been prepared."
    )
    assert factory_calls == [preferences]
    assert len(graph_calls) == 1
    assert graph_calls[0]["session"] is agent_session
    assert graph_calls[0]["planner_decision"] is None
    assert graph_calls[0]["critic_decision"] is None
    assert graph_calls[0]["last_failure"] is None
    assert graph_calls[0]["consecutive_failures"] == 0
    assert session.working_memory == {
        "trip_preferences": {
            "intent": "trip_planning",
            "destination": "Kandy",
            "start_date": None,
            "end_date": None,
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
        ("assistant", "Your trip itinerary has been prepared."),
    ]


@pytest.mark.parametrize(
    ("status", "itinerary", "expected_text"),
    [
        (AgentSessionStatus.COMPLETED, {"days": []}, "itinerary"),
        (AgentSessionStatus.BEST_EFFORT, None, "best-effort"),
        (AgentSessionStatus.INFEASIBLE, None, "could not be satisfied"),
        (AgentSessionStatus.FAILED, None, "could not be completed"),
    ],
)
def test_response_for_planning_session_maps_terminal_statuses(
    status, itinerary, expected_text
):
    response = chat_router._response_for_planning_session(
        AgentSession(goal="Plan a trip", status=status, itinerary=itinerary)
    )

    assert expected_text in response


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
