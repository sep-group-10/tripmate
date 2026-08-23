from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import ApiError, ErrorCode
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.common import ApiResponse
from app.schemas.user import UserRegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user is not None:
        raise ApiError(ErrorCode.EMAIL_ALREADY_EXISTS, "Email is already registered")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ApiError(
            ErrorCode.EMAIL_ALREADY_EXISTS, "Email is already registered"
        ) from exc
    db.refresh(user)

    return ApiResponse(data=user)


_DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing-safety")


@router.post("/login", response_model=ApiResponse[UserResponse])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    password_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH
    password_is_valid = verify_password(payload.password, password_hash)

    if user is None or not password_is_valid:
        raise ApiError(ErrorCode.INVALID_CREDENTIALS, "Invalid email or password")

    return ApiResponse(data=user)
