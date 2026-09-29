import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    """Natural-language message sent to a planning session."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=4000)

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, value: str) -> str:
        """Reject messages that contain only whitespace."""
        if not value.strip():
            raise ValueError("Message cannot be blank or only whitespace")
        return value


class PlanningSessionInfo(BaseModel):
    """Planning-session details returned with a chat response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    iteration_count: int
    progress_message: str | None
    progress_percentage: int


class ChatItineraryItem(BaseModel):
    candidate_id: str
    category: str
    name: str
    start_time: str
    end_time: str
    latitude: float | None = None
    longitude: float | None = None
    duration_minutes: int | None = None
    opening_hours: Any = None


class ChatItineraryDay(BaseModel):
    day_number: int
    date: str
    day_type: str
    items: list[ChatItineraryItem]
    hotel_id: str | None = None
    hotel_location: dict[str, Any] | None = None
    warnings: list[str]
    route_optimization: dict[str, Any] | None = None


class ChatUnscheduledItem(BaseModel):
    candidate_id: str
    name: str
    category: str
    reason: str


class ChatItinerary(BaseModel):
    status: str
    days: list[ChatItineraryDay]
    hotel_by_destination: dict[str, str]
    unscheduled: list[ChatUnscheduledItem]
    warnings: list[str]


class ChatResponse(BaseModel):
    """Assistant reply and any structured itinerary produced by planning."""

    assistant_message: str
    session: PlanningSessionInfo
    itinerary: ChatItinerary | None = None
