from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentSessionStatus(str, Enum):
    COMPLETED = "completed"
    BEST_EFFORT = "best_effort"
    INFEASIBLE = "infeasible"
    FAILED = "failed"


class AgentSession(BaseModel):
    user_request: str
    trip_preferences: dict[str, Any] = Field(default_factory=dict)
    tool_results: list[dict[str, Any]] = Field(default_factory=list)
    tool_execution_order: list[str] = Field(default_factory=list)
    iteration_count: int = 0
    status: AgentSessionStatus | None = None
