import uuid

from sqlalchemy.orm import Session

from app.models.trip import Trip
from app.models.user import User
from app.schemas.preference import PreferenceResult


def create_trip(
    db: Session,
    user_id: uuid.UUID,
    preferences: PreferenceResult,
) -> Trip:
    """Create a persistent Trip from completed preferences and user defaults."""
    user = db.get(User, user_id)
    if user is None:
        raise ValueError("Authenticated user does not exist")

    if (
        preferences.start_date is None
        or preferences.end_date is None
        or preferences.duration_days is None
        or preferences.budget is None
    ):
        raise ValueError("Completed preferences are missing required Trip fields")

    trip = Trip(
        user_id=user_id,
        travel_start_date=preferences.start_date,
        travel_end_date=preferences.end_date,
        duration=preferences.duration_days,
        budget=preferences.budget,
        travel_style=user.preferred_travel_style or "standard",
        accommodation_preference=user.preferred_accommodation or "unspecified",
    )
    db.add(trip)
    db.flush()
    return trip
