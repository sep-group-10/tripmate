from pydantic import BaseModel, EmailStr, field_validator

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class LoginData(BaseModel):
    access_token: str
    user: UserResponse
