from datetime import date
from decimal import Decimal

import pytest

from app.schemas.preference import PreferenceResult
from app.services.agent_session import create_agent_session


def _complete_preferences() -> PreferenceResult:
    return PreferenceResult(
        intent="trip_planning",
        destination="Kandy",
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 12),
        duration_days=3,
        budget=Decimal("50000.00"),
        travelers=2,
        interests=["culture", "nature"],
        transport_type="train",
    )


def test_create_agent_session_from_complete_trip_preferences():
    preferences = _complete_preferences()

    session = create_agent_session(preferences)

    assert session.goal == "Plan a trip to Kandy"
    assert session.trip_requirements == {
        "destination": "Kandy",
        "start_date": date(2026, 12, 10),
        "end_date": date(2026, 12, 12),
        "duration_days": 3,
        "budget": Decimal("50000.00"),
        "travelers": 2,
        "interests": ["culture", "nature"],
        "transport_type": "train",
    }


def test_create_agent_session_copies_all_preference_fields_without_mutation():
    preferences = _complete_preferences()

    session = create_agent_session(preferences)
    session.trip_requirements["interests"].append("food")

    assert preferences.interests == ["culture", "nature"]
    assert session.trip_requirements["interests"] == ["culture", "nature", "food"]


def test_create_agent_session_uses_generic_goal_without_destination():
    preferences = PreferenceResult(intent="trip_planning")

    session = create_agent_session(preferences)

    assert session.goal == "Plan a trip"


def test_create_agent_session_rejects_incomplete_preferences():
    preferences = PreferenceResult(
        intent="trip_planning",
        destination="Kandy",
        missing_fields=["dates", "budget"],
    )

    with pytest.raises(ValueError, match="complete trip preferences"):
        create_agent_session(preferences)


def test_create_agent_session_rejects_normal_conversation():
    preferences = PreferenceResult(intent="normal_conversation")

    with pytest.raises(ValueError, match="trip planning preferences"):
        create_agent_session(preferences)


def test_create_agent_session_uses_agent_session_defaults():
    session = create_agent_session(_complete_preferences())

    assert session.tool_results == []
    assert session.tool_execution_order == []
    assert session.iteration_count == 0
    assert session.status is None
