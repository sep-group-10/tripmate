import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.common import UTCTimestamp
from app.schemas.user import UserResponse


class UserListData(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class UserListResponse(BaseModel):
    success: bool = True
    data: UserListData


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    rating: int
    comment: str | None
    status: str
    created_at: UTCTimestamp


class FeedbackStatusUpdate(BaseModel):
    status: Literal["pending", "resolved"]


class AdminStats(BaseModel):
    total_users: int
    pending_feedback_count: int
    draft_trips_count: int
    destinations_count: int


class MonthPoint(BaseModel):
    label: str
    trips: int
    users: int


class TripsGrowthData(BaseModel):
    months: list[MonthPoint]


class ActivityEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    kind: str
    title: str
    meta: str | None
    created_at: UTCTimestamp
