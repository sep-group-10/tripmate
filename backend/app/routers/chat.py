import uuid

from fastapi import APIRouter, Depends
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.errors import ApiError, ErrorCode
from app.models.conversation_history import ConversationHistory
from app.models.planning_session import PlanningSession
from app.models.user import User
from app.schemas.agent_session import AgentSession, AgentSessionStatus
from app.schemas.chat import (
    ChatItinerary,
    ChatRequest,
    ChatResponse,
    PlanningSessionInfo,
)
from app.schemas.common import ApiResponse
from app.schemas.preference import PreferenceResult
from app.services.agent_session import create_agent_session
from app.services.chat_response_generator import ChatResponseGenerator
from app.services.conversation_history import get_conversation, save_message
from app.services.final_response_generator import FinalResponseGenerator
from app.services.langgraph.planning_graph import planning_graph
from app.services.preference_processor import PreferenceProcessor
from app.services.trip_service import create_trip

router = APIRouter(prefix="/chat", tags=["chat"])


def _to_langchain_messages(
    conversation: list[ConversationHistory],
) -> list[BaseMessage]:
    """Convert persisted conversation messages into LangChain messages."""

    messages: list[BaseMessage] = []
    for entry in conversation:
        if entry.role == "user":
            messages.append(HumanMessage(content=entry.message))
        elif entry.role == "assistant":
            messages.append(AIMessage(content=entry.message))
        else:
            raise ValueError(f"Unsupported conversation role: {entry.role}")

    return messages


def _itinerary_for_agent_session(session: AgentSession) -> ChatItinerary | None:
    """Select the effective schedule unless planning failed or was infeasible."""

    if session.status in {AgentSessionStatus.FAILED, AgentSessionStatus.INFEASIBLE}:
        return None

    for tool_name in ("route_optimizer", "scheduling_engine"):
        result = next(
            (
                entry.get("result")
                for entry in reversed(session.tool_results)
                if entry.get("tool") == tool_name
            ),
            None,
        )
        if result is not None:
            return ChatItinerary.model_validate(result)
    return None


def _prepare_preferences_for_planning(
    db: Session,
    planning_session: PlanningSession,
    preferences: PreferenceResult,
) -> None:
    """Persist JSON-compatible preferences for the future planning flow."""

    working_memory = dict(planning_session.working_memory or {})
    working_memory["trip_preferences"] = preferences.model_dump(mode="json")
    planning_session.working_memory = working_memory
    db.commit()
    db.refresh(planning_session)


def _process_chat_message(
    db: Session,
    planning_session: PlanningSession,
    message: str,
    current_user: User,
) -> ChatResponse:
    """Store, process, and reply to one user message in a planning session."""

    save_message(db, planning_session.id, "user", message)
    conversation = get_conversation(db, planning_session.id)
    preferences = PreferenceProcessor().process(_to_langchain_messages(conversation))
    itinerary = None

    if preferences.intent == "trip_planning" and not preferences.missing_fields:
        if planning_session.trip_id is None:
            trip = create_trip(db, current_user.id, preferences)
            planning_session.trip_id = trip.id
            db.commit()
            db.refresh(planning_session)
        _prepare_preferences_for_planning(db, planning_session, preferences)
        agent_session = create_agent_session(preferences)
        planning_result = planning_graph.invoke(
            {
                "session": agent_session,
                "planner_decision": None,
                "critic_decision": None,
                "last_failure": None,
                "consecutive_failures": 0,
            }
        )
        final_agent_session = planning_result["session"]

        planning_session.status = final_agent_session.status.value
        planning_session.iteration_count = final_agent_session.iteration_count
        db.commit()
        db.refresh(planning_session)

        assistant_message = FinalResponseGenerator().generate(final_agent_session)
        itinerary = _itinerary_for_agent_session(final_agent_session)
    else:
        assistant_message = ChatResponseGenerator().generate(
            _to_langchain_messages(conversation), preferences
        )
        if assistant_message is None:
            raise RuntimeError("No chat response is required for complete preferences")

    save_message(db, planning_session.id, "assistant", assistant_message)

    return ChatResponse(
        assistant_message=assistant_message,
        session=PlanningSessionInfo.model_validate(planning_session),
        itinerary=itinerary,
    )


@router.post("", response_model=ApiResponse[ChatResponse])
def start_chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a planning session and accept the user's first message."""
    planning_session = PlanningSession(
        user_id=current_user.id,
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
        data=_process_chat_message(db, planning_session, payload.message, current_user)
    )


@router.post("/{session_id}", response_model=ApiResponse[ChatResponse])
def send_message(
    session_id: uuid.UUID,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept and process a message for an existing planning session."""
    planning_session = (
        db.query(PlanningSession)
        .filter(
            PlanningSession.id == session_id,
            PlanningSession.user_id == current_user.id,
        )
        .first()
    )
    if planning_session is None:
        raise ApiError(ErrorCode.NOT_FOUND, "Planning session not found")

    return ApiResponse(
        data=_process_chat_message(db, planning_session, payload.message, current_user)
    )
