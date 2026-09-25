import uuid

import pytest

from app.models.conversation_history import ConversationHistory
from app.models.planning_session import PlanningSession
from app.services.conversation_history import get_conversation, save_message


def _planning_session(db_session) -> PlanningSession:
    """Create the minimum planning session required for history tests."""
    session = PlanningSession(
        trip_id=None,
        status="pending",
        iteration_count=0,
        progress_message=None,
        progress_percentage=0,
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


def test_save_user_message(db_session):
    session = _planning_session(db_session)

    saved_message = save_message(
        db=db_session,
        session_id=session.id,
        role="user",
        message="I want to visit Kandy",
    )

    stored_message = db_session.get(ConversationHistory, saved_message.id)
    assert stored_message is not None
    assert stored_message.planning_session_id == session.id
    assert stored_message.role == "user"
    assert stored_message.message == "I want to visit Kandy"
    assert stored_message.created_at is not None


def test_save_assistant_message(db_session):
    session = _planning_session(db_session)

    saved_message = save_message(
        db=db_session,
        session_id=session.id,
        role="assistant",
        message="Kandy is a great destination for a cultural trip.",
    )

    assert saved_message.planning_session_id == session.id
    assert saved_message.role == "assistant"
    assert saved_message.message == "Kandy is a great destination for a cultural trip."
    assert saved_message.created_at is not None


def test_get_conversation_returns_chronological_order(db_session):
    session = _planning_session(db_session)

    save_message(
        db=db_session,
        session_id=session.id,
        role="user",
        message="I want to visit Kandy",
    )
    save_message(
        db=db_session,
        session_id=session.id,
        role="assistant",
        message="Kandy has many cultural attractions.",
    )
    save_message(
        db=db_session,
        session_id=session.id,
        role="user",
        message="Please include the Temple of the Tooth.",
    )

    conversation = get_conversation(db=db_session, session_id=session.id)

    assert [(entry.role, entry.message) for entry in conversation] == [
        ("user", "I want to visit Kandy"),
        ("assistant", "Kandy has many cultural attractions."),
        ("user", "Please include the Temple of the Tooth."),
    ]


def test_get_conversation_isolates_sessions(db_session):
    session_a = _planning_session(db_session)
    session_b = _planning_session(db_session)

    save_message(
        db=db_session,
        session_id=session_a.id,
        role="user",
        message="Plan a trip to Kandy.",
    )
    save_message(
        db=db_session,
        session_id=session_b.id,
        role="user",
        message="Plan a trip to Galle.",
    )
    save_message(
        db=db_session,
        session_id=session_a.id,
        role="assistant",
        message="Here is a Kandy itinerary.",
    )

    conversation = get_conversation(db=db_session, session_id=session_a.id)

    assert [(entry.role, entry.message) for entry in conversation] == [
        ("user", "Plan a trip to Kandy."),
        ("assistant", "Here is a Kandy itinerary."),
    ]
    assert all(entry.planning_session_id == session_a.id for entry in conversation)


def test_save_message_missing_session(db_session):
    with pytest.raises(ValueError, match="Planning session not found"):
        save_message(
            db=db_session,
            session_id=uuid.uuid4(),
            role="user",
            message="I want to visit Kandy",
        )
