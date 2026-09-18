from typing import Any

from pydantic import BaseModel, Field


class PlannerDecision(BaseModel):
    action: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class CriticDecision(BaseModel):
    # Tells the graph whether planning should continue or finish.
    continue_planning: bool

    # The final status when the planning process should stop.
    status: str | None = None

    # Optional explanation from the critic.
    reason: str | None = None
