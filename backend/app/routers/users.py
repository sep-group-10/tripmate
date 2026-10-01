from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.feedback import Feedback
from app.models.trip import Trip
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.export import UserDataExport
from app.schemas.profile import ProfileUpdateRequest
from app.schemas.user import UserResponse
from app.services.image_upload import upload_image

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


@router.post("/me/profile-picture", response_model=ApiResponse[UserResponse])
def upload_my_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Resize and store a new profile picture for the current user,
    replacing any previous one."""
    url = upload_image(file, key_prefix=f"profiles/{current_user.id}")

    current_user.profile_picture_url = url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return ApiResponse(data=current_user)


@router.delete("/me/profile-picture", response_model=ApiResponse[UserResponse])
def remove_my_profile_picture(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Unlink the current user's profile picture. The S3 object itself
    is left in place - only the reference on the user row is cleared."""
    current_user.profile_picture_url = None
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return ApiResponse(data=current_user)


@router.get("/me/export", response_model=ApiResponse[UserDataExport])
def export_my_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export all personal data the system holds about the current
    user - profile, trips, and feedback - as a single JSON document."""
    trips = db.query(Trip).filter(Trip.user_id == current_user.id).all()
    feedback = db.query(Feedback).filter(Feedback.user_id == current_user.id).all()

    return ApiResponse(
        data=UserDataExport(
            profile=current_user,
            trips=trips,
            feedback=feedback,
        )
    )
