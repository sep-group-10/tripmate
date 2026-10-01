import uuid
from typing import TypedDict

from sqlalchemy.orm import Session


class PlanningContext(TypedDict):
    """Request-scoped dependencies shared with planning graph nodes."""

    db: Session
    planning_session_id: uuid.UUID
