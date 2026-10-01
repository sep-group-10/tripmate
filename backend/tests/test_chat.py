"""Integration tests for the chat preference-processing flow."""

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from langchain_core.tools import tool

from app.core.dependencies import get_current_user
from app.main import app
from app.models.conversation_history import ConversationHistory
from app.models.planning_session import PlanningSession
from app.models.trip import Trip
from app.routers import chat as chat_router
from app.schemas.agent_session import AgentSession, AgentSessionStatus
from app.schemas.planning import CriticDecision, PlannerDecision
from app.schemas.preference import PreferenceResult
from app.services.agent_session import create_agent_session
from app.services.langgraph import critic as critic_module
from app.services.langgraph import planner as planner_module
from app.services.preference_processor import PreferenceProcessor
from app.services.tools import registry

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


class FakeStructuredPreferenceModel:
    """Return structured results to the real PreferenceProcessor without Gemini."""

    def __init__(self, results):
        self.results = list(results)
        self.prompts = []

    def invoke(self, prompt):
        self.prompts.append(prompt)
        return self.results.pop(0)


def _mock_real_preference_processor(monkeypatch, *results):
    processor = PreferenceProcessor.__new__(PreferenceProcessor)
    processor.model = FakeStructuredPreferenceModel(results)
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


def _install_deterministic_planning_graph(
    monkeypatch, preferences, *, include_weather=True
):
    """Use the real LangGraph with deterministic Planner, Critic, and tools."""
    agent_session = create_agent_session(preferences)
    requirements = agent_session.trip_requirements
    start_date = requirements["start_date"]
    end_date = requirements["end_date"]
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = date.fromisoformat(end_date)

    days = []
    for day_number in range((end_date - start_date).days + 1):
        current_date = start_date + timedelta(days=day_number)
        days.append(
            {
                "day_number": day_number + 1,
                "date": current_date.isoformat(),
                "day_type": "day_trip",
                "items": [
                    {
                        "candidate_id": f"place-{day_number + 1}",
                        "category": "attraction",
                        "name": f"Kandy cultural site {day_number + 1}",
                        "start_time": "09:00",
                        "end_time": "10:00",
                        "latitude": 7.2906,
                        "longitude": 80.6337,
                        "duration_minutes": 60,
                        "opening_hours": None,
                    }
                ],
                "hotel_id": "hotel-1",
                "hotel_location": None,
                "warnings": [],
            }
        )
    schedule = {
        "status": "ok",
        "days": days,
        "hotel_by_destination": {},
        "unscheduled": [],
        "warnings": [],
    }

    @tool
    def scheduling_engine(candidates: list[dict], trip_requirements: dict) -> dict:
        """Return a valid deterministic itinerary for this integration test."""
        return schedule

    @tool
    def weather_validator(schedule: dict) -> dict:
        """Return a deterministic successful weather result."""
        return {"status": "ok", "days": [], "warnings": []}

    @tool
    def cost_estimator(
        itinerary: dict, candidates: list[dict], trip_requirements: dict
    ) -> dict:
        """Return a deterministic cost estimate within the supplied budget."""
        categories = (
            "transport_intercity",
            "transport_local",
            "accommodation",
            "activities",
            "dining",
            "miscellaneous",
            "total",
        )
        return {
            **{category: {"min": 100, "max": 200} for category in categories},
            "travellers": 2,
            "warnings": [],
        }

    monkeypatch.setitem(registry.TOOLS, "scheduling_engine", scheduling_engine)
    if include_weather:
        monkeypatch.setitem(registry.TOOLS, "weather_validator", weather_validator)
    monkeypatch.setitem(registry.TOOLS, "cost_estimator", cost_estimator)

    decisions = [
        PlannerDecision(action="candidate_retriever"),
        PlannerDecision(action="scoring_engine"),
        PlannerDecision(action="scheduling_engine"),
        PlannerDecision(action="route_optimizer"),
    ]
    if include_weather:
        decisions.append(PlannerDecision(action="weather_validator"))
    decisions.append(PlannerDecision(action="cost_estimator"))

    class FakePlannerModel:
        def __init__(self):
            self.prompts = []

        def invoke(self, prompt):
            self.prompts.append(prompt)
            return decisions[len(self.prompts) - 1]

    class FakeCriticModel:
        def __init__(self):
            self.prompts = []

        def invoke(self, prompt):
            self.prompts.append(prompt)
            assessment = {
                "score": 4,
                "reasoning": "The plan is balanced across all days.",
            }
            return CriticDecision(
                continue_planning=False,
                status="completed",
                reason="The itinerary meets the requested trip constraints.",
                variety=assessment,
                daily_balance=assessment,
                interest_match=assessment,
                pacing=assessment,
                suggestions=[],
            )

    planner_model = FakePlannerModel()
    critic_model = FakeCriticModel()
    monkeypatch.setattr(
        planner_module, "create_planner_model", lambda _runnable_actions: planner_model
    )
    monkeypatch.setattr(critic_module, "create_critic_model", lambda: critic_model)
    return planner_model, critic_model


def test_start_chat_processes_normal_conversation_and_stores_messages(
    client, db_session, monkeypatch
):
    processor = _mock_real_preference_processor(
        monkeypatch,
        PreferenceResult(intent="normal_conversation", missing_fields=["budget"]),
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
        json={"message": "Hi, what can you do?"},
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
    assert processor.model.prompts[0][-1].content == "human: Hi, what can you do?"
    assert "normal_conversation" in str(processor.model.prompts[0][0].content)
    assert factory_calls == []
    assert graph_calls == []
    assert len(response_generator.calls) == 1
    assert response_generator.calls[0][1].intent == "normal_conversation"
    assert db_session.query(Trip).count() == 0
    assert [
        (entry.role, entry.message)
        for entry in _conversation(db_session, session["id"])
    ] == [
        ("user", "Hi, what can you do?"),
        ("assistant", expected_reply),
    ]


def test_preferences_missing_required_trip_values_do_not_create_trip(
    client, db_session, monkeypatch
):
    response_generator = _mock_response_generator(
        monkeypatch,
        "What dates, trip length, budget, group size, and activities do you prefer?",
    )
    processor = _mock_real_preference_processor(
        monkeypatch,
        PreferenceResult(
            intent="trip_planning",
            destination="Kandy",
            missing_fields=[],
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

    response = client.post(CHAT_URL, json={"message": "I want to visit Kandy."})

    assert response.status_code == 200
    expected_reply = (
        "What dates, trip length, budget, group size, and activities do you prefer?"
    )
    assert response.json()["data"]["assistant_message"] == expected_reply
    assert processor.model.prompts[0][-1].content == "human: I want to visit Kandy."
    assert processor.model.results == []
    assert response.json()["data"]["itinerary"] is None
    assert db_session.query(Trip).count() == 0
    assert factory_calls == []
    assert graph_calls == []
    assert [
        entry.message
        for entry in _conversation(db_session, response.json()["data"]["session"]["id"])
        if entry.role == "assistant"
    ] == [expected_reply]
    assert response_generator.calls[0][1].missing_fields == [
        "dates",
        "duration_days",
        "budget",
        "travelers",
        "interests",
        "transport_type",
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
        user_id=user.id,
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


def test_session_owner_can_continue_their_chat_session(
    client, db_session, existing_user, monkeypatch
):
    session = _planning_session(db_session, existing_user)
    _mock_processor(
        monkeypatch,
        PreferenceResult(
            intent="trip_planning", destination="Kandy", missing_fields=["dates"]
        ),
    )
    _mock_response_generator(monkeypatch, "Which dates would you prefer?")

    response = client.post(
        f"{CHAT_URL}/{session.id}", json={"message": "I want to visit Kandy."}
    )

    assert response.status_code == 200
    assert response.json()["data"]["session"]["id"] == str(session.id)
    assert [
        (entry.role, entry.message) for entry in _conversation(db_session, session.id)
    ] == [
        ("user", "I want to visit Kandy."),
        ("assistant", "Which dates would you prefer?"),
    ]


def test_another_user_cannot_access_chat_session(
    client, db_session, existing_user, other_user, monkeypatch
):
    session = _planning_session(db_session, existing_user)
    _mock_processor(
        monkeypatch,
        PreferenceResult(
            intent="trip_planning", destination="Kandy", missing_fields=["dates"]
        ),
    )
    app.dependency_overrides[get_current_user] = lambda: other_user

    response = client.post(
        f"{CHAT_URL}/{session.id}", json={"message": "Show me the plan."}
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert _conversation(db_session, session.id) == []


def test_cross_user_chat_cannot_create_or_modify_victim_trip(
    client, db_session, existing_user, other_user, monkeypatch
):
    session = _planning_session(db_session, existing_user)
    victim_trip = db_session.get(Trip, session.trip_id)
    session.trip_id = None
    db_session.commit()
    original_trip = {
        "user_id": victim_trip.user_id,
        "status": victim_trip.status,
        "travel_start_date": victim_trip.travel_start_date,
        "travel_end_date": victim_trip.travel_end_date,
        "budget": victim_trip.budget,
    }
    original_trip_count = db_session.query(Trip).count()
    create_trip_calls = []
    monkeypatch.setattr(
        chat_router,
        "create_trip",
        lambda *args, **kwargs: create_trip_calls.append((args, kwargs)),
    )
    _mock_processor(monkeypatch, _complete_preferences())
    app.dependency_overrides[get_current_user] = lambda: other_user

    response = client.post(
        f"{CHAT_URL}/{session.id}", json={"message": "Plan this trip for me."}
    )

    db_session.refresh(session)
    db_session.refresh(victim_trip)
    assert response.status_code == 404
    assert create_trip_calls == []
    assert db_session.query(Trip).count() == original_trip_count
    assert session.trip_id is None
    assert session.working_memory is None
    assert {
        "user_id": victim_trip.user_id,
        "status": victim_trip.status,
        "travel_start_date": victim_trip.travel_start_date,
        "travel_end_date": victim_trip.travel_end_date,
        "budget": victim_trip.budget,
    } == original_trip
    assert _conversation(db_session, session.id) == []


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


def test_multi_message_preference_collection_starts_planning_only_when_complete(
    client, db_session, existing_user, monkeypatch
):
    preferences_by_turn = [
        PreferenceResult(intent="trip_planning", destination="Kandy"),
        PreferenceResult(intent="trip_planning", destination="Kandy", duration_days=3),
        PreferenceResult(
            intent="trip_planning", destination="Kandy", duration_days=3, travelers=2
        ),
        PreferenceResult(
            intent="trip_planning",
            destination="Kandy",
            duration_days=3,
            travelers=2,
            budget=Decimal("50000"),
        ),
        PreferenceResult(
            intent="trip_planning",
            destination="Kandy",
            duration_days=3,
            travelers=2,
            budget=Decimal("50000"),
            interests=["culture"],
        ),
        PreferenceResult(
            intent="trip_planning",
            destination="Kandy",
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 3),
            duration_days=3,
            travelers=2,
            budget=Decimal("50000"),
            interests=["culture"],
        ),
        _complete_preferences(),
    ]
    processor = _mock_real_preference_processor(monkeypatch, *preferences_by_turn)
    clarification_texts = [f"Please share preference {index}." for index in range(1, 7)]
    response_generator = _mock_response_generator(monkeypatch, *clarification_texts)
    preferences = _complete_preferences()
    planner_model, critic_model = _install_deterministic_planning_graph(
        monkeypatch, preferences
    )

    first_response = client.post(CHAT_URL, json={"message": "I want to visit Kandy."})
    session_id = first_response.json()["data"]["session"]["id"]
    later_messages = [
        "For 3 days.",
        "Two people.",
        "My budget is 50,000.",
        "I like cultural attractions.",
        "October 1 to 3, 2026.",
        "I prefer the train.",
    ]
    responses = [first_response]
    for message in later_messages:
        responses.append(
            client.post(f"{CHAT_URL}/{session_id}", json={"message": message})
        )

    assert all(response.status_code == 200 for response in responses)
    assert [call[1].missing_fields for call in response_generator.calls] == [
        [
            "dates",
            "duration_days",
            "budget",
            "travelers",
            "interests",
            "transport_type",
        ],
        ["dates", "budget", "travelers", "interests", "transport_type"],
        ["dates", "budget", "interests", "transport_type"],
        ["dates", "interests", "transport_type"],
        ["dates", "transport_type"],
        ["transport_type"],
    ]
    assert db_session.query(Trip).count() == 1
    assert planner_model.prompts and len(planner_model.prompts) == 6
    assert len(critic_model.prompts) == 1

    all_turns_prompt = processor.model.prompts[-1][-1].content
    for message in ["I want to visit Kandy.", *later_messages[:-1]]:
        assert message in all_turns_prompt
    assert clarification_texts[-1] in all_turns_prompt
    assert [
        (entry.role, entry.message) for entry in _conversation(db_session, session_id)
    ] == [
        ("user", "I want to visit Kandy."),
        ("assistant", clarification_texts[0]),
        ("user", "For 3 days."),
        ("assistant", clarification_texts[1]),
        ("user", "Two people."),
        ("assistant", clarification_texts[2]),
        ("user", "My budget is 50,000."),
        ("assistant", clarification_texts[3]),
        ("user", "I like cultural attractions."),
        ("assistant", clarification_texts[4]),
        ("user", "October 1 to 3, 2026."),
        ("assistant", clarification_texts[5]),
        ("user", "I prefer the train."),
        ("assistant", responses[-1].json()["data"]["assistant_message"]),
    ]
    assert responses[-1].json()["data"]["session"]["status"] == "completed"
    assert (
        responses[-1].json()["data"]["assistant_message"]
        == _conversation(db_session, session_id)[-1].message
    )


def test_complete_single_message_runs_chat_api_through_real_planning_graph(
    client, db_session, existing_user, monkeypatch
):
    preferences = _complete_preferences()
    processor = _mock_real_preference_processor(monkeypatch, preferences)
    planner_model, critic_model = _install_deterministic_planning_graph(
        monkeypatch, preferences, include_weather=False
    )

    response = client.post(
        CHAT_URL,
        json={
            "message": (
                "Plan a three-day trip to Kandy from October 1 to 3 for two people, "
                "budget 50,000, focused on culture, and travel by train."
            )
        },
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["session"]["status"] == "completed"
    assert "Your trip plan is ready." in body["assistant_message"]
    assert "Kandy cultural site 1" in body["assistant_message"]
    assert "2026-10-01" in body["assistant_message"]
    assert "100–200" in body["assistant_message"]
    assert body["itinerary"]["days"][0]["items"][0]["name"] == "Kandy cultural site 1"
    assert len(planner_model.prompts) == 5
    assert len(critic_model.prompts) == 1
    assert "cost_estimator" in critic_model.prompts[0]
    assert "weather_validator" not in critic_model.prompts[0]
    assert processor.model.prompts[0][-1].content.startswith(
        "human: Plan a three-day trip"
    )
    assert db_session.query(Trip).count() == 1
    assert [
        (entry.role, entry.message)
        for entry in _conversation(db_session, body["session"]["id"])
    ] == [
        (
            "user",
            "Plan a three-day trip to Kandy from October 1 to 3 for two people, "
            "budget 50,000, focused on culture, and travel by train.",
        ),
        ("assistant", body["assistant_message"]),
    ]


def test_chat_sessions_keep_conversation_history_isolated(
    client, db_session, monkeypatch
):
    processor = _mock_processor(
        monkeypatch,
        PreferenceResult(intent="normal_conversation"),
        PreferenceResult(intent="normal_conversation"),
        PreferenceResult(intent="normal_conversation"),
    )
    _mock_response_generator(monkeypatch, "A reply.", "B reply.", "A follow-up reply.")

    response_a = client.post(CHAT_URL, json={"message": "Session A first message."})
    response_b = client.post(CHAT_URL, json={"message": "Session B first message."})
    session_a_id = response_a.json()["data"]["session"]["id"]
    session_b_id = response_b.json()["data"]["session"]["id"]
    follow_up_a = client.post(
        f"{CHAT_URL}/{session_a_id}", json={"message": "Session A follow-up."}
    )

    assert (
        response_a.status_code
        == response_b.status_code
        == follow_up_a.status_code
        == 200
    )
    assert session_a_id != session_b_id
    assert [message.content for message in processor.calls[0]] == [
        "Session A first message."
    ]
    assert [message.content for message in processor.calls[1]] == [
        "Session B first message."
    ]
    assert [(message.type, message.content) for message in processor.calls[2]] == [
        ("human", "Session A first message."),
        ("ai", "A reply."),
        ("human", "Session A follow-up."),
    ]
    assert [
        (entry.role, entry.message) for entry in _conversation(db_session, session_a_id)
    ] == [
        ("user", "Session A first message."),
        ("assistant", "A reply."),
        ("user", "Session A follow-up."),
        ("assistant", "A follow-up reply."),
    ]
    assert [
        (entry.role, entry.message) for entry in _conversation(db_session, session_b_id)
    ] == [
        ("user", "Session B first message."),
        ("assistant", "B reply."),
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
        def invoke(self, state, context=None):
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


@pytest.mark.parametrize(
    ("status", "expected_name"),
    [
        (AgentSessionStatus.COMPLETED, "Optimized place"),
        (AgentSessionStatus.BEST_EFFORT, "Optimized place"),
        (AgentSessionStatus.FAILED, None),
        (AgentSessionStatus.INFEASIBLE, None),
    ],
)
def test_chat_itinerary_selection_respects_final_status(status, expected_name):
    schedule = _schedule_result("Scheduled place")
    optimized = _schedule_result(
        "Optimized place",
        {"reordered": True, "warning": None, "local_distance_km": 1.25},
    )
    session = AgentSession(
        goal="Plan a trip",
        status=status,
        tool_results=[
            {"tool": "scheduling_engine", "result": schedule},
            {"tool": "route_optimizer", "result": optimized},
            # Selection is by preferred tool type, even if a later scheduler
            # result is present in the history.
            {"tool": "scheduling_engine", "result": _schedule_result("Later schedule")},
        ],
    )

    selected = chat_router._itinerary_for_agent_session(session)

    if expected_name is None:
        assert selected is None
    else:
        assert selected is not None
        assert selected.days[0].items[0].name == expected_name
        assert selected.days[0].route_optimization["local_distance_km"] == 1.25

    fallback = chat_router._itinerary_for_agent_session(
        AgentSession(
            goal="Plan a trip",
            status=status,
            tool_results=[{"tool": "scheduling_engine", "result": schedule}],
        )
    )
    if expected_name is None:
        assert fallback is None
    else:
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
