import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.common import UTCTimestamp
from app.schemas.user import UserResponse


class TripExportItem(BaseModel):
    """One trip, as included in a user's data export."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    travel_start_date: date
    travel_end_date: date
    duration: int
    budget: Decimal
    travel_style: str
    accommodation_preference: str


class FeedbackExportItem(BaseModel):
    """One feedback entry, as included in a user's data export."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rating: int
    comment: str | None
    status: str
    created_at: UTCTimestamp
    updated_at: UTCTimestamp


class UserDataExport(BaseModel):
    """Everything personal data the system holds about one user."""

    profile: UserResponse
    trips: list[TripExportItem]
    feedback: list[FeedbackExportItem]
