import uuid

from sqlalchemy.orm import Session

from app.models.conversation_history import ConversationHistory
from app.models.planning_session import PlanningSession


def save_message(
    db: Session,
    session_id: uuid.UUID,
    role: str,
    message: str,
) -> ConversationHistory:
    """Store a message for an existing planning session."""

    planning_session = (
        db.query(PlanningSession).filter(PlanningSession.id == session_id).first()
    )

    if planning_session is None:
        raise ValueError(f"Planning session not found: {session_id}")

    conversation_message = ConversationHistory(
        planning_session_id=session_id,
        role=role,
        message=message,
    )

    db.add(conversation_message)
    db.commit()
    db.refresh(conversation_message)

    return conversation_message


def get_conversation(
    db: Session,
    session_id: uuid.UUID,
) -> list[ConversationHistory]:
    """Retrieve a planning session's messages in chronological order."""

    return (
        db.query(ConversationHistory)
        .filter(ConversationHistory.planning_session_id == session_id)
        .order_by(ConversationHistory.created_at.asc())
        .all()
    )
