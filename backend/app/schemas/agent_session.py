from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentSessionStatus(str, Enum):
    COMPLETED = "completed"
    BEST_EFFORT = "best_effort"
    INFEASIBLE = "infeasible"
    FAILED = "failed"


class AgentSession(BaseModel):
    goal: str
    trip_requirements: dict[str, Any] = Field(default_factory=dict)

    candidates: list[dict[str, Any]] = Field(default_factory=list)
    ranked_candidates: list[dict[str, Any]] = Field(default_factory=list)
    itinerary: dict[str, Any] | None = None
    optimised_route: dict[str, Any] | None = None
    constraint_result: dict[str, Any] | None = None

    tool_results: list[dict[str, Any]] = Field(default_factory=list)
    tool_execution_order: list[str] = Field(default_factory=list)

    iteration_count: int = 0
    status: AgentSessionStatus | None = None
