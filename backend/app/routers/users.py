from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.profile import ProfileUpdateRequest
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=ApiResponse[UserResponse])
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return ApiResponse(data=current_user)


@router.put("/me", response_model=ApiResponse[UserResponse])
def update_my_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update editable fields on the current user's own profile.
    Role, email, and account status cannot be changed here (rejected
    by ProfileUpdateRequest itself)."""
    # applied_fields() only includes fields the client actually sent, so
    # an omitted field is left as-is instead of being overwritten with None.
    for field, value in payload.applied_fields().items():
        setattr(current_user, field, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return ApiResponse(data=current_user)
