import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import ApiError, ErrorCode
from app.models.planning_session import PlanningSession
from app.schemas.chat import ChatRequest, ChatResponse, PlanningSessionInfo
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ApiResponse[ChatResponse])
def start_chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
):
    """Create a planning session and accept the user's first message."""
    planning_session = PlanningSession(
        trip_id=None,
        status="pending",
        iteration_count=0,
        progress_message=None,
        progress_percentage=0,
    )

    db.add(planning_session)
    db.commit()
    db.refresh(planning_session)

    return ApiResponse(
        data=ChatResponse(
            assistant_message="Thanks! I received your message.",
            session=PlanningSessionInfo.model_validate(planning_session),
        )
    )


@router.post("/{session_id}", response_model=ApiResponse[ChatResponse])
def send_message(
    session_id: uuid.UUID,
    payload: ChatRequest,
    db: Session = Depends(get_db),
):
    """Accept a message for an existing planning session.

    Assistant generation will be connected in a later iteration; this
    endpoint currently returns a stable placeholder response.
    """
    planning_session = db.get(PlanningSession, session_id)
    if planning_session is None:
        raise ApiError(ErrorCode.NOT_FOUND, "Planning session not found")

    return ApiResponse(
        data=ChatResponse(
            assistant_message="Thanks! I received your message.",
            session=PlanningSessionInfo.model_validate(planning_session),
        )
    )
