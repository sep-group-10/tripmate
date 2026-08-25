from uuid import UUID

from sqlalchemy.orm import Session

from app.models.conversation_history import ConversationHistory


def add_message(
    db: Session,
    planning_session_id: UUID,
    role: str,
    message: str,
) -> ConversationHistory:
    """Store a user or assistant message for a planning session."""

    history = ConversationHistory(
        planning_session_id=planning_session_id,
        role=role,
        message=message,
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history


def get_messages(
    db: Session,
    planning_session_id: UUID,
) -> list[ConversationHistory]:
    """Return conversation messages in chronological order."""

    return (
        db.query(ConversationHistory)
        .filter(
            ConversationHistory.planning_session_id == planning_session_id,
        )
        .order_by(ConversationHistory.created_at.asc())
        .all()
    )
