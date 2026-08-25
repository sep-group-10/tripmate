from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from app.models.conversation_history import ConversationHistory
from app.models.planning_session import PlanningSession
from app.models.trip import Trip
from app.services.conversation_history import add_message, get_messages


def create_planning_session(db_session, user_id):
    trip = Trip(
        user_id=user_id,
        status="draft",
        travel_start_date=date(2026, 9, 10),
        travel_end_date=date(2026, 9, 12),
        duration=3,
        budget=Decimal("100000.00"),
        travel_style="cultural",
        accommodation_preference="hotel",
    )

    db_session.add(trip)
    db_session.flush()

    planning_session = PlanningSession(
        trip_id=trip.id,
        status="active",
    )

    db_session.add(planning_session)
    db_session.commit()
    db_session.refresh(planning_session)

    return planning_session


def test_add_user_message(db_session, existing_user):
    planning_session = create_planning_session(
        db_session,
        existing_user.id,
    )

    result = add_message(
        db=db_session,
        planning_session_id=planning_session.id,
        role="user",
        message="I want to visit Kandy.",
    )

    assert result.planning_session_id == planning_session.id
    assert result.role == "user"
    assert result.message == "I want to visit Kandy."


def test_add_assistant_message(db_session, existing_user):
    planning_session = create_planning_session(
        db_session,
        existing_user.id,
    )

    result = add_message(
        db=db_session,
        planning_session_id=planning_session.id,
        role="assistant",
        message="How many days are you planning?",
    )

    assert result.planning_session_id == planning_session.id
    assert result.role == "assistant"
    assert result.message == "How many days are you planning?"


def test_get_messages_returns_session_history(db_session, existing_user):
    planning_session = create_planning_session(
        db_session,
        existing_user.id,
    )

    add_message(
        db_session,
        planning_session.id,
        "user",
        "I want to visit Kandy.",
    )
    add_message(
        db_session,
        planning_session.id,
        "assistant",
        "How many days?",
    )

    messages = get_messages(
        db_session,
        planning_session.id,
    )

    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].message == "I want to visit Kandy."
    assert messages[1].role == "assistant"
    assert messages[1].message == "How many days?"


def test_get_messages_returns_chronological_order(
    db_session,
    existing_user,
):
    planning_session = create_planning_session(
        db_session,
        existing_user.id,
    )

    first = ConversationHistory(
        planning_session_id=planning_session.id,
        role="user",
        message="First message",
        created_at=datetime.now(UTC),
    )

    second = ConversationHistory(
        planning_session_id=planning_session.id,
        role="assistant",
        message="Second message",
        created_at=datetime.now(UTC) + timedelta(seconds=1),
    )

    db_session.add_all([second, first])
    db_session.commit()

    messages = get_messages(
        db_session,
        planning_session.id,
    )

    assert [message.message for message in messages] == [
        "First message",
        "Second message",
    ]


def test_get_messages_only_returns_requested_session(
    db_session,
    existing_user,
):
    first_session = create_planning_session(
        db_session,
        existing_user.id,
    )
    second_session = create_planning_session(
        db_session,
        existing_user.id,
    )

    add_message(
        db_session,
        first_session.id,
        "user",
        "First session message",
    )
    add_message(
        db_session,
        second_session.id,
        "user",
        "Second session message",
    )

    messages = get_messages(
        db_session,
        first_session.id,
    )

    assert len(messages) == 1
    assert messages[0].message == "First session message"
