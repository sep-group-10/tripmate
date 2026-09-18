from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.security import validate_password_strength
from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """Request body for POST /auth/login."""

    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Lowercase the email so login matches registration regardless
        of how the user types their email's case."""
        return value.lower()


class LoginData(BaseModel):
    """Response data for a successful login."""

    access_token: str
    refresh_token: str
    user: UserResponse


class RefreshRequest(BaseModel):
    """Request body for POST /auth/refresh."""

    refresh_token: str


class RefreshData(BaseModel):
    """Response data for a successful token refresh."""

    access_token: str
    refresh_token: str


class LogoutRequest(BaseModel):
    """Request body for POST /auth/logout."""

    refresh_token: str | None = None


class ChangePasswordRequest(BaseModel):
    """Request body for POST /auth/change-password."""

    current_password: str
    new_password: str = Field(min_length=8, max_length=72)

    @field_validator("new_password")
    @classmethod
    def new_password_strength(cls, value: str) -> str:
        validate_password_strength(value)
        return value
