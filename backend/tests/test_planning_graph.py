import inspect

from app.schemas.agent_session import AgentSession, AgentSessionStatus
from app.schemas.planning import CriticDecision, PlannerDecision
from app.services.langgraph import critic, planner
from app.services.langgraph.planning_graph import (
    planning_graph,
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
        goal="Plan a trip to Kandy",
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


def test_planning_graph_flow(monkeypatch):
    """Verify the real Planner → Tool → Critic → END flow."""

    class FakeModel:
        def __init__(self, response):
            self.response = response

        def invoke(self, prompt):
            return self.response

    monkeypatch.setattr(
        planner,
        "create_planner_model",
        lambda: FakeModel(PlannerDecision(action="placeholder_tool", arguments={})),
    )
    monkeypatch.setattr(
        critic,
        "create_critic_model",
        lambda: FakeModel(CriticDecision(continue_planning=False, status="completed")),
    )

    session = AgentSession(
        goal="Plan a simple one-day trip to Kandy.",
        trip_requirements={"destination": "Kandy", "duration_days": 1},
    )

    result = planning_graph.invoke(
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


def test_real_planner_uses_current_agent_session_fields(monkeypatch):
    class FakeModel:
        def __init__(self):
            self.prompts = []

        def invoke(self, prompt):
            self.prompts.append(prompt)
            return PlannerDecision(action="placeholder_tool", arguments={})

    model = FakeModel()
    monkeypatch.setattr(planner, "create_planner_model", lambda: model)
    session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy", "duration_days": 3},
    )

    result = planner.planner_node(
        {
            "session": session,
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }
    )

    assert result["planner_decision"].action == "placeholder_tool"
    assert session.iteration_count == 1
    assert "Plan a trip to Kandy" in model.prompts[0]
    assert "'destination': 'Kandy'" in model.prompts[0]


def test_real_critic_uses_current_agent_session_fields(monkeypatch):
    class FakeModel:
        def __init__(self):
            self.prompts = []

        def invoke(self, prompt):
            self.prompts.append(prompt)
            return CriticDecision(continue_planning=False, status="completed")

    model = FakeModel()
    monkeypatch.setattr(critic, "create_critic_model", lambda: model)
    session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy", "duration_days": 3},
    )

    result = critic.critic_node(
        {
            "session": session,
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }
    )

    assert result["critic_decision"].status == "completed"
    assert "Plan a trip to Kandy" in model.prompts[0]
    assert "'destination': 'Kandy'" in model.prompts[0]


def test_planning_components_do_not_reference_removed_session_fields():
    for component in (planner, critic):
        source = inspect.getsource(component)
        assert "session.user_request" not in source
        assert "session.trip_preferences" not in source


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
