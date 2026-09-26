from decimal import Decimal

import pytest
from langchain_core.messages import HumanMessage

from app.schemas.preference import PreferenceResult
from app.services.preference_processor import PreferenceProcessor


class FakeModel:
    """Return a predefined structured-model response without calling Gemini."""

    def __init__(self, result):
        self.result = result

    def invoke(self, prompt):
        return self.result


def _processor_with_result(result) -> PreferenceProcessor:
    """Create a processor with a fake model and no Gemini initialization."""
    processor = PreferenceProcessor.__new__(PreferenceProcessor)
    processor.model = FakeModel(result)
    return processor


def test_preference_processor_returns_preference_result():
    expected_result = PreferenceResult(
        intent="trip_planning",
        destination="Kandy",
        missing_fields=[],
    )
    processor = _processor_with_result(expected_result)

    result = processor.process([HumanMessage(content="I want to visit Kandy.")])

    assert isinstance(result, PreferenceResult)
    assert result == expected_result


def test_preference_processor_extracts_trip_preferences():
    processor = _processor_with_result(
        PreferenceResult(
            intent="trip_planning",
            destination="Kandy",
            duration_days=3,
            budget=Decimal("50000.00"),
            travelers=2,
            interests=["culture", "nature"],
            transport_type="train",
            missing_fields=[],
        )
    )

    result = processor.process(
        [
            HumanMessage(
                content=(
                    "Plan a three-day Kandy trip for two people with a "
                    "50000 LKR budget focused on culture and nature."
                )
            )
        ]
    )

    assert result.intent == "trip_planning"
    assert result.destination == "Kandy"
    assert result.duration_days == 3
    assert result.budget == Decimal("50000.00")
    assert result.travelers == 2
    assert result.interests == ["culture", "nature"]
    assert result.transport_type == "train"
    assert result.missing_fields == []


def test_preference_processor_handles_normal_conversation():
    processor = _processor_with_result(
        PreferenceResult(
            intent="normal_conversation",
            missing_fields=[],
        )
    )

    result = processor.process([HumanMessage(content="Hello, how are you?")])

    assert result.intent == "normal_conversation"
    assert result.missing_fields == []


def test_preference_processor_reports_missing_trip_preferences():
    processor = _processor_with_result(
        PreferenceResult(
            intent="trip_planning",
            destination="Kandy",
            missing_fields=["duration_days", "budget", "travelers", "transport_type"],
        )
    )

    result = processor.process([HumanMessage(content="I want to visit Kandy.")])

    assert result.intent == "trip_planning"
    assert result.destination == "Kandy"
    assert result.missing_fields == [
        "duration_days",
        "budget",
        "travelers",
        "transport_type",
    ]


def test_preference_processor_rejects_invalid_model_response():
    processor = _processor_with_result({"intent": "trip_planning"})

    with pytest.raises(TypeError, match="invalid preference result"):
        processor.process([HumanMessage(content="Plan a trip to Kandy.")])
