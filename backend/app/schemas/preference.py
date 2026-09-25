from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class PreferenceResult(BaseModel):
    """Structured trip preferences extracted from conversation history."""

    intent: Literal["trip_planning", "normal_conversation"]

    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    duration_days: int | None = None
    budget: Decimal | None = None
    travelers: int | None = None
    interests: list[str] = Field(default_factory=list)

    missing_fields: list[str] = Field(default_factory=list)
