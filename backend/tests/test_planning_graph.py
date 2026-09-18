from langgraph.graph import END, START, StateGraph

from app.schemas.agent_session import AgentSession, AgentSessionStatus
from app.schemas.planning import CriticDecision, PlannerDecision
from app.services.langgraph.planning_graph import (
    PlanningState,
    route_after_critic,
    tool_execution_node,
)


def create_state(
    *,
    iteration_count=1,
    max_iterations=8,
    continue_planning=True,
    status=None,
    consecutive_failures=0,
):
    """Create a small fake graph state for testing routing."""
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

    # Remove the value to verify that the graph uses its default of 8.
    state.pop("max_iterations")

    result = route_after_critic(state)

    assert result == "end"
    assert state["session"].status == AgentSessionStatus.BEST_EFFORT


def test_planning_graph_flow():
    """Verify the complete Planner → Tool → Critic → END flow."""

    def fake_planner(state: PlanningState) -> dict:
        # Simulate Gemini selecting the placeholder tool.
        return {
            "planner_decision": PlannerDecision(
                action="placeholder_tool",
                arguments={},
            )
        }

    def fake_critic(state: PlanningState) -> dict:
        # Simulate the Critic deciding that planning is complete.
        state["session"].status = AgentSessionStatus.COMPLETED

        return {
            "critic_decision": None,
        }

    graph_builder = StateGraph(PlanningState)

    graph_builder.add_node("planner", fake_planner)
    graph_builder.add_node("tool_execution", tool_execution_node)
    graph_builder.add_node("critic", fake_critic)

    # Verify the complete Planner → Tool → Critic flow.
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
