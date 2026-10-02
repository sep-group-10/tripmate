import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

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


class AdminCreateRequest(BaseModel):
    """Request body for POST /admin/admins. Super-admin-only: creates an
    ADMIN account (the system has exactly one super admin, so this
    never creates one) with no password, and emails an invite link for
    the new admin to set one."""

    full_name: str
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("full_name")
    @classmethod
    def full_name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Full name cannot be blank or only whitespace")
        return value


class AdminCreateData(BaseModel):
    """Response data for a successful admin creation - no password is
    issued here, the invited admin sets their own via email."""

    email: str
    message: str


class AdminStatusUpdate(BaseModel):
    """Request body for PATCH /admin/admins/{admin_id}/status."""

    is_active: bool


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    rating: int
    comment: str | None
    status: str
    resolution_outcome: str | None
    resolution_note: str | None
    resolved_by_name: str | None
    resolved_at: UTCTimestamp | None
    created_at: UTCTimestamp


class FeedbackResolveRequest(BaseModel):
    """Request body for PATCH /admin/feedback/{feedback_id}/resolve."""

    outcome: Literal["Fixed the data", "Shared with team", "No action needed"]
    note: str | None = None


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
