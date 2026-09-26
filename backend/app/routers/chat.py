import uuid

from fastapi import APIRouter, Depends
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import ApiError, ErrorCode
from app.models.conversation_history import ConversationHistory
from app.models.planning_session import PlanningSession
from app.schemas.agent_session import AgentSession, AgentSessionStatus
from app.schemas.chat import ChatRequest, ChatResponse, PlanningSessionInfo
from app.schemas.common import ApiResponse
from app.schemas.preference import PreferenceResult
from app.services.agent_session import create_agent_session
from app.services.conversation_history import get_conversation, save_message
from app.services.langgraph.planning_graph import planning_graph
from app.services.preference_processor import PreferenceProcessor

router = APIRouter(prefix="/chat", tags=["chat"])

MISSING_FIELD_QUESTIONS = {
    "destination": "Where would you like to travel?",
    "dates": "When are you planning to travel?",
    "duration_days": "How many days would you like to travel?",
    "budget": "What is your budget for the trip?",
    "travelers": "How many people will be traveling?",
    "interests": "What activities or interests would you like to include?",
    "transport_type": "Which transport type do you prefer?",
}


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


def _response_for_preferences(preferences: PreferenceResult) -> str:
    """Build a deterministic response from extracted trip preferences."""

    if preferences.intent == "normal_conversation":
        return "Hello! How can I help you today?"

    if preferences.missing_fields:
        questions = [
            MISSING_FIELD_QUESTIONS[field] for field in preferences.missing_fields
        ]
        return " ".join(questions)

    return "Your trip preferences are ready for planning."


def _response_for_planning_session(session: AgentSession) -> str:
    """Build a safe, deterministic response from the final planning state."""

    if session.status == AgentSessionStatus.COMPLETED:
        if session.itinerary:
            return "Your trip itinerary has been prepared."
        return "Your trip plan has been prepared."
    if session.status == AgentSessionStatus.BEST_EFFORT:
        return "A best-effort trip plan has been prepared."
    if session.status == AgentSessionStatus.INFEASIBLE:
        return "Your requested trip constraints could not be satisfied."
    if session.status == AgentSessionStatus.FAILED:
        return "Trip planning could not be completed."
    return "Your trip planning request has been processed."


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
) -> ChatResponse:
    """Store, process, and reply to one user message in a planning session."""

    save_message(db, planning_session.id, "user", message)
    conversation = get_conversation(db, planning_session.id)
    preferences = PreferenceProcessor().process(_to_langchain_messages(conversation))

    if preferences.intent == "trip_planning" and not preferences.missing_fields:
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

        assistant_message = _response_for_planning_session(final_agent_session)
    else:
        assistant_message = _response_for_preferences(preferences)

    save_message(db, planning_session.id, "assistant", assistant_message)

    return ChatResponse(
        assistant_message=assistant_message,
        session=PlanningSessionInfo.model_validate(planning_session),
    )


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
        data=_process_chat_message(db, planning_session, payload.message)
    )


@router.post("/{session_id}", response_model=ApiResponse[ChatResponse])
def send_message(
    session_id: uuid.UUID,
    payload: ChatRequest,
    db: Session = Depends(get_db),
):
    """Accept and process a message for an existing planning session."""
    planning_session = db.get(PlanningSession, session_id)
    if planning_session is None:
        raise ApiError(ErrorCode.NOT_FOUND, "Planning session not found")

    return ApiResponse(
        data=_process_chat_message(db, planning_session, payload.message)
    )
