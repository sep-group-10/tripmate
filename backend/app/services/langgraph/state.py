from typing import NotRequired, TypedDict

from app.schemas.agent_session import AgentSession
from app.schemas.planning import CriticDecision, PlannerDecision


class PlanningState(TypedDict):
    """Shared state passed between LangGraph planning nodes."""

    session: AgentSession
    current_itinerary: NotRequired[dict | None]
    latest_user_message: NotRequired[str]
    max_iterations: NotRequired[int]
    constraint_validation_current: NotRequired[bool]
    planner_decision: PlannerDecision | None
    critic_decision: CriticDecision | None
    last_failure: str | None
    consecutive_failures: int
