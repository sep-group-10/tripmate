from datetime import date
from decimal import Decimal

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from app.models.planning_session import PlanningSession
from app.models.trip import Trip
from app.schemas.agent_session import AgentSession, AgentSessionStatus
from app.schemas.planning import CriticDecision, PlannerDecision
from app.services.conversation_history import add_message, get_messages
from app.services.langgraph.planning_graph import (
    PlanningState,
    route_after_critic,
    tool_execution_node,
)
from app.services.preference_processor import process_preferences


def create_state(
    *,
    iteration_count=1,
    max_iterations=8,
    continue_planning=True,
    status=None,
    consecutive_failures=0,
):
    """Create a small fake graph state for testing."""
    session = AgentSession(
        user_request="Plan a trip to Kandy",
        iteration_count=iteration_count,
    )

    decision = CriticDecision(
        continue_planning=continue_planning,
        status=status,
    )

    return {
        "session": session,
        "messages": [
            HumanMessage(content="Plan a trip to Kandy"),
        ],
        "max_iterations": max_iterations,
        "planner_decision": None,
        "critic_decision": decision,
        "last_failure": None,
        "consecutive_failures": consecutive_failures,
    }


def test_critic_can_route_back_to_planner():
    state = create_state(continue_planning=True)

    result = route_after_critic(state)

    assert result == "planner"


def test_critic_can_finish_with_completed_status():
    state = create_state(
        continue_planning=False,
        status="completed",
    )

    result = route_after_critic(state)

    assert result == "end"
    assert state["session"].status == AgentSessionStatus.COMPLETED


def test_graph_stops_at_maximum_iterations():
    state = create_state(
        iteration_count=8,
        max_iterations=8,
        continue_planning=True,
    )

    result = route_after_critic(state)

    assert result == "end"
    assert state["session"].status == AgentSessionStatus.BEST_EFFORT


def test_graph_stops_after_repeated_failures():
    state = create_state(
        consecutive_failures=2,
        continue_planning=True,
    )

    result = route_after_critic(state)

    assert result == "end"
    assert state["session"].status == AgentSessionStatus.FAILED


def test_critic_can_finish_with_infeasible_status():
    state = create_state(
        continue_planning=False,
        status="infeasible",
    )

    result = route_after_critic(state)

    assert result == "end"
    assert state["session"].status == AgentSessionStatus.INFEASIBLE


def test_graph_uses_default_max_iterations():
    state = create_state(
        iteration_count=8,
        continue_planning=True,
    )

    state.pop("max_iterations")

    result = route_after_critic(state)

    assert result == "end"
    assert state["session"].status == AgentSessionStatus.BEST_EFFORT


def test_planning_graph_flow():
    """Verify the complete Planner → Tool → Critic → END flow."""

    def fake_planner(state: PlanningState) -> dict:
        return {
            "planner_decision": PlannerDecision(
                action="placeholder_tool",
                arguments={},
            )
        }

    def fake_critic(state: PlanningState) -> dict:
        state["session"].status = AgentSessionStatus.COMPLETED

        return {
            "critic_decision": None,
        }

    graph_builder = StateGraph(PlanningState)

    graph_builder.add_node("planner", fake_planner)
    graph_builder.add_node("tool_execution", tool_execution_node)
    graph_builder.add_node("critic", fake_critic)

    graph_builder.add_edge(START, "planner")
    graph_builder.add_edge("planner", "tool_execution")
    graph_builder.add_edge("tool_execution", "critic")
    graph_builder.add_edge("critic", END)

    graph = graph_builder.compile()

    session = AgentSession(
        user_request="Plan a simple one-day trip to Kandy.",
    )

    result = graph.invoke(
        {
            "session": session,
            "messages": [
                HumanMessage(
                    content="Plan a simple one-day trip to Kandy.",
                )
            ],
            "max_iterations": 8,
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }
    )

    assert result["session"].status == AgentSessionStatus.COMPLETED
    assert result["session"].tool_execution_order == ["placeholder_tool"]
    assert len(result["session"].tool_results) == 1
    assert (
        result["session"].tool_results[0]["result"]
        == "Placeholder tool executed successfully."
    )


def test_planner_can_execute_preference_processor():
    """Verify Planner selection executes PreferenceProcessor."""

    session = AgentSession(
        user_request="Plan a trip to Kandy.",
    )

    state = {
        "session": session,
        "messages": [
            HumanMessage(
                content=(
                    "I want to visit Kandy for 3 days. "
                    "There will be 2 travelers. "
                    "Our budget is medium. "
                    "We like culture."
                )
            )
        ],
        "max_iterations": 8,
        "planner_decision": PlannerDecision(
            action="preference_processor",
            arguments={},
        ),
        "critic_decision": None,
        "last_failure": None,
        "consecutive_failures": 0,
    }

    result = tool_execution_node(state)

    assert result["session"].trip_preferences["destination"] == "Kandy"
    assert result["session"].trip_preferences["travelers"] == 2
    assert result["session"].trip_preferences["budget"] == "medium"
    assert "culture" in result["session"].trip_preferences["interests"]

    assert result["session"].tool_execution_order == ["preference_processor"]

    assert len(result["session"].tool_results) == 1
    assert result["session"].tool_results[0]["tool"] == "preference_processor"


def test_real_conversation_history_to_preference_processor(
    db_session,
    existing_user,
):
    """Verify database conversation reaches PreferenceProcessor."""

    trip = Trip(
        user_id=existing_user.id,
        status="draft",
        travel_start_date=date(2026, 9, 10),
        travel_end_date=date(2026, 9, 12),
        duration=3,
        budget=Decimal("100000.00"),
        travel_style="cultural",
        accommodation_preference="hotel",
    )

    db_session.add(trip)
    db_session.flush()

    planning_session = PlanningSession(
        trip_id=trip.id,
        status="active",
    )

    db_session.add(planning_session)
    db_session.commit()
    db_session.refresh(planning_session)

    add_message(
        db_session,
        planning_session.id,
        "user",
        "I want to visit Kandy for 3 days.",
    )

    add_message(
        db_session,
        planning_session.id,
        "assistant",
        "How many travelers are going?",
    )

    add_message(
        db_session,
        planning_session.id,
        "user",
        "There will be 2 travelers. My budget is medium and I like culture.",
    )

    stored_messages = get_messages(
        db_session,
        planning_session.id,
    )

    assert len(stored_messages) == 3

    messages = []

    for stored_message in stored_messages:
        if stored_message.role == "user":
            messages.append(HumanMessage(content=stored_message.message))
        elif stored_message.role == "assistant":
            messages.append(AIMessage(content=stored_message.message))

    result = process_preferences(messages)

    assert result.destination == "Kandy"
    assert result.dates == "3 days"
    assert result.travelers == 2
    assert result.budget == "medium"
    assert "culture" in result.interests
    assert result.missing_fields == []


def test_different_failures_reset_consecutive_failure_count():
    """Different failures must not be treated as a deadlock."""

    state = create_state(
        consecutive_failures=1,
        continue_planning=True,
    )

    state["last_failure"] = "Unknown tool: first_tool"
    state["planner_decision"] = PlannerDecision(
        action="second_tool",
        arguments={},
    )

    result = tool_execution_node(state)

    assert result["last_failure"] == "Unknown tool: second_tool"
    assert result["consecutive_failures"] == 1


def test_same_failure_increments_consecutive_failure_count():
    """The same failure must increase the deadlock counter."""

    state = create_state(
        consecutive_failures=1,
        continue_planning=True,
    )

    failure = "Unknown tool: missing_tool"
    state["last_failure"] = failure
    state["planner_decision"] = PlannerDecision(
        action="missing_tool",
        arguments={},
    )

    result = tool_execution_node(state)

    assert result["last_failure"] == failure
    assert result["consecutive_failures"] == 2
