from langchain_core.messages import HumanMessage

from app.schemas.preferences import TripPreferences
from app.services.preference_processor import process_preferences


def test_complete_conversation_extracts_preferences():
    messages = [
        HumanMessage(
            content=(
                "I want to visit Kandy for 3 days. "
                "There will be 2 travelers. "
                "Our budget is medium. "
                "We are interested in culture and nature."
            )
        )
    ]

    result = process_preferences(messages)

    assert isinstance(result, TripPreferences)
    assert result.destination == "Kandy"
    assert result.dates is not None
    assert result.travelers == 2
    assert result.budget == "medium"
    assert "culture" in result.interests
    assert "nature" in result.interests
    assert result.missing_fields == []


def test_incomplete_conversation_reports_missing_fields():
    messages = [
        HumanMessage(
            content="I want to visit Kandy for 3 days.",
        )
    ]

    result = process_preferences(messages)

    assert isinstance(result, TripPreferences)
    assert result.destination == "Kandy"
    assert result.dates is not None
    assert result.travelers is None
    assert result.budget is None
    assert result.interests == []

    assert "travelers" in result.missing_fields
    assert "budget" in result.missing_fields
    assert "interests" in result.missing_fields


def test_processor_uses_multiple_messages():
    messages = [
        HumanMessage(content="I want to visit Kandy."),
        HumanMessage(content="We are going for 3 days."),
        HumanMessage(content="There will be 2 travelers."),
        HumanMessage(content="Our budget is medium."),
        HumanMessage(content="We like culture and nature."),
    ]

    result = process_preferences(messages)

    assert result.destination == "Kandy"
    assert result.dates is not None
    assert result.travelers == 2
    assert result.budget == "medium"
    assert "culture" in result.interests
    assert "nature" in result.interests
    assert result.missing_fields == []


def test_processor_does_not_invent_missing_information():
    messages = [
        HumanMessage(
            content="I want to visit Kandy.",
        )
    ]

    result = process_preferences(messages)

    assert result.destination == "Kandy"
    assert result.dates is None
    assert result.travelers is None
    assert result.budget is None
    assert result.interests == []

    assert "dates" in result.missing_fields
    assert "travelers" in result.missing_fields
    assert "budget" in result.missing_fields
    assert "interests" in result.missing_fields
