import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.errors import ApiError, ErrorCode
from app.models.agent_execution_trace import AgentExecutionTrace
from app.models.conversation_history import ConversationHistory
from app.models.itinerary import Itinerary
from app.models.itinerary_day import ItineraryDay
from app.models.itinerary_day_item import ItineraryDayItem
from app.models.planning_session import PlanningSession
from app.models.trip import Trip
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.trip import (
    ItineraryDayItemResponse,
    ItineraryDayResponse,
    ItineraryDetailsResponse,
    TripDetailsResponse,
    TripRenameRequest,
    TripResponse,
    TripResumeResponse,
)
from app.services.conversation_history import get_conversation

router = APIRouter(prefix="/trips", tags=["trips"])


def _owned_trip(db: Session, trip_id: uuid.UUID, user_id: uuid.UUID) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if trip is None:
        raise ApiError(ErrorCode.NOT_FOUND, "Trip not found")
    return trip


@router.get("", response_model=ApiResponse[list[TripResponse]])
def list_my_trips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return trips owned by the authenticated user, newest activity first."""
    trips = (
        db.query(Trip)
        .filter(Trip.user_id == current_user.id)
        .order_by(Trip.updated_at.desc(), Trip.created_at.desc())
        .all()
    )
    return ApiResponse(data=trips)


@router.get("/{trip_id}", response_model=ApiResponse[TripDetailsResponse])
def get_my_trip_details(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return an owned trip and its persisted itinerary, if one exists."""
    trip = _owned_trip(db, trip_id, current_user.id)
    planning_session = (
        db.query(PlanningSession)
        .filter(
            PlanningSession.trip_id == trip.id,
            PlanningSession.user_id == current_user.id,
        )
        .first()
    )
    preferences = (
        (planning_session.working_memory or {}).get("trip_preferences", {})
        if planning_session
        else {}
    )
    destination = (
        preferences.get("destination") if isinstance(preferences, dict) else None
    )

    itinerary_record = (
        db.query(Itinerary)
        .filter(Itinerary.trip_id == trip.id)
        .order_by(Itinerary.created_at.desc(), Itinerary.id.desc())
        .first()
    )
    itinerary_details = None
    if itinerary_record is not None:
        day_records = (
            db.query(ItineraryDay)
            .filter(ItineraryDay.itinerary_id == itinerary_record.id)
            .order_by(ItineraryDay.day_number)
            .all()
        )
        days = []
        for day in day_records:
            items = (
                db.query(ItineraryDayItem)
                .filter(ItineraryDayItem.itinerary_day_id == day.id)
                .order_by(ItineraryDayItem.sort_order)
                .all()
            )
            days.append(
                ItineraryDayResponse.model_validate(
                    {
                        **{
                            key: getattr(day, key)
                            for key in (
                                "id",
                                "day_number",
                                "date",
                                "title",
                                "summary",
                            )
                        },
                        "items": [
                            ItineraryDayItemResponse.model_validate(item)
                            for item in items
                        ],
                    }
                )
            )
        itinerary_details = ItineraryDetailsResponse(
            id=itinerary_record.id,
            total_estimated_cost=itinerary_record.total_estimated_cost,
            route_info=itinerary_record.route_info,
            weather_info=itinerary_record.weather_info,
            share_token=itinerary_record.share_token,
            days=days,
        )

    return ApiResponse(
        data=TripDetailsResponse(
            id=trip.id,
            title=trip.title,
            destination=destination,
            travel_start_date=trip.travel_start_date,
            travel_end_date=trip.travel_end_date,
            duration=trip.duration,
            budget=trip.budget,
            status=trip.status,
            itinerary=itinerary_details,
        )
    )


@router.patch("/{trip_id}/title", response_model=ApiResponse[TripResponse])
def rename_my_draft_trip(
    trip_id: uuid.UUID,
    payload: TripRenameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rename a draft owned by the authenticated user."""
    trip = _owned_trip(db, trip_id, current_user.id)
    if trip.status != "draft":
        raise ApiError(ErrorCode.VALIDATION_ERROR, "Only draft trips can be renamed")
    if not payload.title:
        raise HTTPException(status_code=422, detail="Trip title cannot be empty")

    trip.title = payload.title
    db.commit()
    db.refresh(trip)
    return ApiResponse(data=trip)


@router.delete("/{trip_id}", response_model=ApiResponse[TripResponse])
def discard_my_draft_trip(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an owned draft and its linked session history and traces."""
    trip = _owned_trip(db, trip_id, current_user.id)
    if trip.status != "draft":
        raise ApiError(ErrorCode.VALIDATION_ERROR, "Only draft trips can be discarded")
    response_trip = TripResponse.model_validate(trip)

    planning_sessions = (
        db.query(PlanningSession)
        .filter(
            PlanningSession.trip_id == trip.id,
            PlanningSession.user_id == current_user.id,
        )
        .all()
    )
    session_ids = [session.id for session in planning_sessions]
    if session_ids:
        db.query(ConversationHistory).filter(
            ConversationHistory.planning_session_id.in_(session_ids)
        ).delete(synchronize_session=False)
        db.query(AgentExecutionTrace).filter(
            AgentExecutionTrace.planning_session_id.in_(session_ids)
        ).delete(synchronize_session=False)
        for planning_session in planning_sessions:
            db.delete(planning_session)

    db.delete(trip)
    db.commit()
    return ApiResponse(data=response_trip)


@router.get("/{trip_id}/resume", response_model=ApiResponse[TripResumeResponse])
def resume_my_draft_trip(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a draft trip's linked session and saved conversation."""
    trip = _owned_trip(db, trip_id, current_user.id)
    if trip.status not in {"draft", "generated"}:
        raise ApiError(
            ErrorCode.VALIDATION_ERROR,
            "Only draft or generated trips can be resumed",
        )

    planning_session = (
        db.query(PlanningSession)
        .filter(
            PlanningSession.trip_id == trip.id,
            PlanningSession.user_id == current_user.id,
        )
        .first()
    )
    if planning_session is None:
        raise ApiError(ErrorCode.NOT_FOUND, "Planning session not found")

    messages = get_conversation(db, planning_session.id)
    return ApiResponse(
        data=TripResumeResponse(
            trip=trip,
            session=planning_session,
            conversation=[
                {
                    "id": message.id,
                    "role": message.role,
                    "message": message.message,
                    "created_at": message.created_at,
                }
                for message in messages
            ],
        )
    )


@router.post("/{trip_id}/save", response_model=ApiResponse[TripResponse])
def save_my_trip(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save an itinerary generated for the authenticated user's trip."""
    trip = _owned_trip(db, trip_id, current_user.id)
    if trip.status != "generated":
        raise ApiError(
            ErrorCode.VALIDATION_ERROR,
            "Only generated trips can be saved",
        )

    trip.status = "saved"
    db.commit()
    db.refresh(trip)
    return ApiResponse(data=trip)


@router.delete("/{trip_id}/save", response_model=ApiResponse[TripResponse])
def unsave_my_trip(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a saved trip to generated for its authenticated owner."""
    trip = _owned_trip(db, trip_id, current_user.id)
    if trip.status != "saved":
        raise ApiError(
            ErrorCode.VALIDATION_ERROR,
            "Only saved trips can be unsaved",
        )

    trip.status = "generated"
    db.commit()
    db.refresh(trip)
    return ApiResponse(data=trip)
