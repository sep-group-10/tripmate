from pydantic import BaseModel, EmailStr

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginData(BaseModel):
    access_token: str
    user: UserResponse
