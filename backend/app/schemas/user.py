import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.common import UTCTimestamp


class UserRegisterRequest(BaseModel):
    """Request body for POST /auth/register."""

    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Lowercase the email so the same address can't be registered
        twice with different casing."""
        return value.lower()

    @field_validator("password")
    @classmethod
    def password_not_blank(cls, value: str) -> str:
        """Reject a password that is only whitespace (min_length alone
        would let e.g. 8 spaces through)."""
        if not value.strip():
            raise ValueError("Password cannot be blank or only whitespace")
        return value

    @field_validator("full_name")
    @classmethod
    def full_name_not_blank(cls, value: str) -> str:
        """Reject a full_name that is only whitespace."""
        if not value.strip():
            raise ValueError("Full name cannot be blank or only whitespace")
        return value


class UserResponse(BaseModel):
    """Public user representation returned by the API. Deliberately
    excludes password_hash and other internal-only fields."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    is_email_verified: bool
    preferred_travel_style: str | None
    preferred_accommodation: str | None
    typical_budget_range: str | None
    interests: list[str] | None
    created_at: UTCTimestamp
