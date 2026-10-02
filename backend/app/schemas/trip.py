import uuid
from datetime import date, time
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.chat import PlanningSessionInfo
from app.schemas.common import UTCTimestamp


class TripResponse(BaseModel):
    """Public representation of a persisted trip."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: Literal["draft", "generated", "saved"]
    title: str | None
    travel_start_date: date | None
    travel_end_date: date | None
    duration: int | None
    budget: Decimal | None
    travel_style: str
    accommodation_preference: str
    created_at: UTCTimestamp
    updated_at: UTCTimestamp


class PlanningConversationMessage(BaseModel):
    id: uuid.UUID
    role: str
    message: str
    created_at: UTCTimestamp


class TripResumeResponse(BaseModel):
    trip: TripResponse
    session: PlanningSessionInfo
    conversation: list[PlanningConversationMessage]


class ItineraryDayItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    item_type: str
    title: str
    description: str | None
    start_time: time | None
    end_time: time | None
    location: str | None
    estimated_cost: Decimal | None
    sort_order: int


class ItineraryDayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    day_number: int
    date: date
    title: str
    summary: str | None
    items: list[ItineraryDayItemResponse]


class ItineraryDetailsResponse(BaseModel):
    id: uuid.UUID
    total_estimated_cost: Decimal
    route_info: dict | None
    weather_info: dict | None
    share_token: str | None
    days: list[ItineraryDayResponse]


class TripDetailsResponse(BaseModel):
    id: uuid.UUID
    title: str | None
    destination: str | None
    travel_start_date: date | None
    travel_end_date: date | None
    duration: int | None
    budget: Decimal | None
    status: Literal["draft", "generated", "saved"]
    itinerary: ItineraryDetailsResponse | None


class TripRenameRequest(BaseModel):
    title: str = Field(max_length=255)

    @field_validator("title")
    @classmethod
    def strip_and_validate_title(cls, value: str) -> str:
        return value.strip()
