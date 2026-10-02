import uuid
from datetime import date, time

from fastapi import APIRouter, Depends
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.errors import ApiError, ErrorCode
from app.models.conversation_history import ConversationHistory
from app.models.itinerary import Itinerary
from app.models.itinerary_day import ItineraryDay
from app.models.itinerary_day_item import ItineraryDayItem
from app.models.planning_session import PlanningSession
from app.models.trip import Trip
from app.models.user import User
from app.schemas.agent_session import AgentSession, AgentSessionStatus
from app.schemas.chat import (
    ChatItinerary,
    ChatRequest,
    ChatResponse,
    PlanningSessionInfo,
)
from app.schemas.common import ApiResponse
from app.schemas.planning import ItineraryEditPlan
from app.schemas.preference import PreferenceResult
from app.services.agent_session import create_agent_session
from app.services.chat_response_generator import ChatResponseGenerator
from app.services.conversation_history import get_conversation, save_message
from app.services.final_response_generator import FinalResponseGenerator
from app.services.itinerary_service import (
    persist_chat_itinerary,
    persist_removed_chat_item,
)
from app.services.langgraph.context import PlanningContext
from app.services.langgraph.planning_graph import planning_graph
from app.services.preference_processor import PreferenceProcessor
from app.services.trip_service import apply_trip_preferences, create_draft_trip

router = APIRouter(prefix="/chat", tags=["chat"])


def _remove_itinerary_item(
    current_itinerary: dict, edit_plan: ItineraryEditPlan
) -> tuple[ChatItinerary | None, uuid.UUID | None, str | None]:
    """Resolve one persisted item and validate the itinerary without it."""
    target = (edit_plan.target_item or "").strip()
    if not target:
        return None, None, "Which itinerary item would you like me to remove?"
    matches = []
    for day_index, day in enumerate(current_itinerary.get("days", [])):
        if (
            edit_plan.source_day is not None
            and day.get("day_number") != edit_plan.source_day
        ):
            continue
        for item_index, item in enumerate(day.get("items", [])):
            if (
                str(item.get("id")) == target
                or item.get("title", "").casefold() == target.casefold()
            ):
                matches.append((day_index, item_index, item))
    if not matches:
        return (
            None,
            None,
            f"I couldn't find '{target}' in that day. Which item did you mean?",
        )
    if len(matches) > 1:
        return (
            None,
            None,
            f"I found more than one '{target}'. Which one should I remove?",
        )

    target_item = matches[0][2]
    days = []
    for day_index, day in enumerate(current_itinerary["days"]):
        context_items = [
            item
            for index, item in enumerate(day.get("items", []))
            if not (
                day_index == matches[0][0] and item.get("id") == target_item.get("id")
            )
        ]
        day_items = []
        for item in context_items:
            try:
                start_time = time.fromisoformat(item["start_time"]).isoformat(
                    timespec="minutes"
                )
                end_time = time.fromisoformat(item["end_time"]).isoformat(
                    timespec="minutes"
                )
            except (KeyError, TypeError, ValueError):
                start_time, end_time = item.get("start_time"), item.get("end_time")
            day_items.append(
                {
                    "candidate_id": item.get("id") or item.get("title"),
                    "category": item.get("item_type") or "activity",
                    "name": item.get("title"),
                    "start_time": start_time,
                    "end_time": end_time,
                    "latitude": None,
                    "longitude": None,
                    "duration_minutes": None,
                    "opening_hours": None,
                }
            )
        days.append(
            {
                "day_number": day["day_number"],
                "date": day["date"],
                "day_type": day.get("title") or "day_trip",
                "items": day_items,
                "hotel_id": None,
                "hotel_location": None,
                "warnings": [],
            }
        )
    try:
        for day in days:
            date.fromisoformat(day["date"])
            previous_end = None
            for item in day["items"]:
                start = time.fromisoformat(item["start_time"])
                end = time.fromisoformat(item["end_time"])
                if end <= start or (previous_end is not None and start < previous_end):
                    raise ValueError("Invalid or overlapping schedule")
                previous_end = end
        itinerary = ChatItinerary(
            status="ok", days=days, hotel_by_destination={}, unscheduled=[], warnings=[]
        )
        return itinerary, uuid.UUID(str(target_item["id"])), None
    except Exception:
        return (
            None,
            None,
            "I couldn't validate the updated schedule, so I left your itinerary unchanged.",
        )


def _current_itinerary_context(db: Session, trip_id: uuid.UUID | None) -> dict | None:
    """Load the newest persisted itinerary as plain data for the planning graph."""
    if trip_id is None:
        return None
    itinerary = (
        db.query(Itinerary)
        .filter(Itinerary.trip_id == trip_id)
        .order_by(Itinerary.created_at.desc(), Itinerary.id.desc())
        .first()
    )
    if itinerary is None:
        return None

    days = (
        db.query(ItineraryDay)
        .filter(ItineraryDay.itinerary_id == itinerary.id)
        .order_by(ItineraryDay.day_number, ItineraryDay.id)
        .all()
    )
    day_context = []
    for day in days:
        items = (
            db.query(ItineraryDayItem)
            .filter(ItineraryDayItem.itinerary_day_id == day.id)
            .order_by(ItineraryDayItem.sort_order, ItineraryDayItem.id)
            .all()
        )
        day_context.append(
            {
                "id": str(day.id),
                "day_number": day.day_number,
                "date": day.date.isoformat(),
                "title": day.title,
                "summary": day.summary,
                "items": [
                    {
                        "id": str(item.id),
                        "item_type": item.item_type,
                        "title": item.title,
                        "description": item.description,
                        "start_time": item.start_time.isoformat()
                        if item.start_time
                        else None,
                        "end_time": item.end_time.isoformat()
                        if item.end_time
                        else None,
                        "sort_order": item.sort_order,
                        "location": item.location,
                        "estimated_cost": str(item.estimated_cost)
                        if item.estimated_cost is not None
                        else None,
                    }
                    for item in items
                ],
            }
        )
    return {
        "id": str(itinerary.id),
        "trip_id": str(itinerary.trip_id),
        "total_estimated_cost": str(itinerary.total_estimated_cost),
        "route_info": itinerary.route_info,
        "weather_info": itinerary.weather_info,
        "days": day_context,
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


def _ensure_draft_trip_for_session(
    db: Session,
    planning_session: PlanningSession,
    current_user: User,
    preferences: PreferenceResult,
) -> None:
    """Create or update the one Trip linked to this authenticated session."""
    locked_session = (
        db.query(PlanningSession)
        .filter(
            PlanningSession.id == planning_session.id,
            PlanningSession.user_id == current_user.id,
        )
        .with_for_update()
        .populate_existing()
        .first()
    )
    if locked_session is None:
        raise ApiError(ErrorCode.NOT_FOUND, "Planning session not found")

    if locked_session.trip_id is None:
        trip = create_draft_trip(db, current_user.id)
        locked_session.trip_id = trip.id
    else:
        trip = (
            db.query(Trip)
            .filter(
                Trip.id == locked_session.trip_id,
                Trip.user_id == current_user.id,
            )
            .first()
        )
        if trip is None:
            raise ApiError(ErrorCode.NOT_FOUND, "Trip not found")

    apply_trip_preferences(trip, preferences)

    working_memory = dict(locked_session.working_memory or {})
    working_memory["trip_preferences"] = preferences.model_dump(mode="json")
    locked_session.working_memory = working_memory
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

    if preferences.intent == "trip_planning":
        _ensure_draft_trip_for_session(db, planning_session, current_user, preferences)

    if preferences.intent == "trip_planning" and not preferences.missing_fields:
        agent_session = create_agent_session(preferences)
        current_itinerary = _current_itinerary_context(db, planning_session.trip_id)
        try:
            planning_result = planning_graph.invoke(
                {
                    "session": agent_session,
                    "current_itinerary": current_itinerary,
                    "latest_user_message": message,
                    "planner_decision": None,
                    "critic_decision": None,
                    "last_failure": None,
                    "consecutive_failures": 0,
                },
                context=PlanningContext(
                    db=db,
                    planning_session_id=planning_session.id,
                ),
            )
        except Exception:
            # Preserve failed tool traces before propagating the graph exception.
            db.commit()
            raise
        final_agent_session = planning_result["session"]

        planner_decision = planning_result.get("planner_decision")
        edit_plan = planner_decision.edit_plan if planner_decision else None
        if edit_plan and edit_plan.operation == "remove":
            edited_itinerary, target_item_id, clarification = _remove_itinerary_item(
                current_itinerary or {"days": []}, edit_plan
            )
            if clarification:
                assistant_message = clarification
                itinerary = None
            else:
                itinerary = edited_itinerary
                assistant_message = (
                    "Done — I removed the item and updated your itinerary."
                )
                if planning_session.trip_id is not None:
                    persist_removed_chat_item(
                        db,
                        planning_session.trip_id,
                        uuid.UUID(current_itinerary["id"]),
                        target_item_id,
                    )
                    db.commit()
            planning_session.status = "completed"
            planning_session.iteration_count = final_agent_session.iteration_count
            db.commit()
            db.refresh(planning_session)
            save_message(db, planning_session.id, "assistant", assistant_message)
            return ChatResponse(
                assistant_message=assistant_message,
                session=PlanningSessionInfo.model_validate(planning_session),
                itinerary=itinerary,
            )

        planning_session.status = final_agent_session.status.value
        planning_session.iteration_count = final_agent_session.iteration_count
        db.commit()
        db.refresh(planning_session)

        assistant_message = FinalResponseGenerator().generate(final_agent_session)
        itinerary = _itinerary_for_agent_session(final_agent_session)
        if itinerary is not None and planning_session.trip_id is not None:
            cost_estimate = next(
                (
                    entry.get("result")
                    for entry in reversed(final_agent_session.tool_results)
                    if isinstance(entry, dict) and entry.get("tool") == "cost_estimator"
                ),
                None,
            )
            persist_chat_itinerary(
                db, planning_session.trip_id, itinerary, cost_estimate
            )
            db.commit()
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
