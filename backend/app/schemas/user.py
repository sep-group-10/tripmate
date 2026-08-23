import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.common import UTCTimestamp


class UserRegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    is_email_verified: bool
    created_at: UTCTimestamp
