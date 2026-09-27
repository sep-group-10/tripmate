from langgraph.graph import END, START, StateGraph

from app.schemas.agent_session import AgentSessionStatus
from app.services.langgraph.critic import critic_node, route_after_critic
from app.services.langgraph.planner import planner_node
from app.services.langgraph.state import PlanningState
from app.services.langgraph.state_validator import validate_planning_state
from app.services.tools.registry import TOOLS


def _latest_tool_result(session, tool_name: str):
    return next(
        (
            entry["result"]
            for entry in reversed(session.tool_results)
            if entry.get("tool") == tool_name
        ),
        None,
    )


def tool_execution_node(state: PlanningState) -> dict:
    """Execute the Planner-selected registered tool and record its result."""

    session = state["session"]
    decision = state["planner_decision"]

    if decision is None:
        failure = "Planner did not provide a tool decision."
        consecutive_failures = (
            state["consecutive_failures"] + 1 if state["last_failure"] == failure else 1
        )
        return {
            "last_failure": failure,
            "consecutive_failures": consecutive_failures,
        }

    tool = TOOLS.get(decision.action)
    if tool is None:
        failure = f"Unknown tool: {decision.action}"
        consecutive_failures = (
            state["consecutive_failures"] + 1 if state["last_failure"] == failure else 1
        )
        return {
            "last_failure": failure,
            "consecutive_failures": consecutive_failures,
        }

    result = tool.invoke(decision.arguments)
    session.tool_results.append(
        {
            "tool": decision.action,
            "result": result,
        }
    )
    session.tool_execution_order.append(decision.action)
    state_update = {
        "session": session,
        "last_failure": None,
        "consecutive_failures": 0,
    }
    if decision.action in {"scheduling_engine", "route_optimizer", "cost_estimator"}:
        session.constraint_result = None
        state_update["constraint_validation_current"] = False
    elif decision.action == "constraint_validator":
        session.constraint_result = result
        state_update["constraint_validation_current"] = False

    return {
        **state_update,
    }


def planning_state_validation_node(state: PlanningState) -> dict:
    """Check the current session structure after each Planner-selected tool."""

    session = state["session"]
    result = validate_planning_state(session)
    session.tool_results.append({"tool": "planning_state_validator", "result": result})
    return {"session": session}


def route_after_planning_state_validation(state: PlanningState) -> str:
    """Replan invalid sessions, preserving graph termination guards."""

    session = state["session"]
    result = _latest_tool_result(session, "planning_state_validator") or {}
    if result.get("status") != "pass":
        if session.iteration_count >= state.get("max_iterations", 8):
            session.status = AgentSessionStatus.BEST_EFFORT
            return "end"
        if state["consecutive_failures"] >= 2:
            session.status = AgentSessionStatus.FAILED
            return "end"
        return "planner"

    next_route = route_after_tool_execution(state)
    if next_route == "constraint_validation":
        return next_route

    # A Critic invocation is allowed only after this graph's automatic
    # constraint node has established a passing result for current inputs.
    constraint_result = session.constraint_result
    validation_is_current = state.get("constraint_validation_current", False)
    if validation_is_current and constraint_result:
        if constraint_result.get("status") == "pass":
            return next_route

    if session.iteration_count >= state.get("max_iterations", 8):
        session.status = AgentSessionStatus.BEST_EFFORT
        return "end"
    if state["consecutive_failures"] >= 2:
        session.status = AgentSessionStatus.FAILED
        return "end"
    return "planner"


def constraint_validation_node(state: PlanningState) -> dict:
    """Validate constraints once scheduling and cost results are available."""

    session = state["session"]
    itinerary = _latest_tool_result(session, "scheduling_engine")
    cost_estimate = _latest_tool_result(session, "cost_estimator")
    result = TOOLS["constraint_validator"].invoke(
        {
            "itinerary": itinerary,
            "trip_requirements": session.trip_requirements,
            "cost_estimate": cost_estimate,
        }
    )
    session.constraint_result = result
    session.tool_results.append({"tool": "constraint_validator", "result": result})
    session.tool_execution_order.append("constraint_validator")
    return {"session": session, "constraint_validation_current": True}


def route_after_tool_execution(state: PlanningState) -> str:
    """Run hard-constraint checks before the Critic sees a completed estimate."""

    session = state["session"]
    decision = state["planner_decision"]
    if (
        decision is not None
        and decision.action == "cost_estimator"
        and _latest_tool_result(session, "scheduling_engine") is not None
        and _latest_tool_result(session, "cost_estimator") is not None
        and session.constraint_result is None
    ):
        return "constraint_validation"
    return "critic"


def route_after_constraint_validation(state: PlanningState) -> str:
    """Replan after failed checks while preserving graph termination guards."""

    session = state["session"]
    result = session.constraint_result
    if (
        state.get("constraint_validation_current", False)
        and result is not None
        and result.get("status") == "pass"
    ):
        return "critic"

    if session.iteration_count >= state.get("max_iterations", 8):
        session.status = AgentSessionStatus.BEST_EFFORT
        return "end"

    if state["consecutive_failures"] >= 2:
        session.status = AgentSessionStatus.FAILED
        return "end"

    return "planner"


def create_planning_graph():
    """Build the Planner → Tool Execution → Critic planning workflow."""

    graph_builder = StateGraph(PlanningState)

    graph_builder.add_node("planner", planner_node)
    graph_builder.add_node("tool_execution", tool_execution_node)
    graph_builder.add_node("planning_state_validation", planning_state_validation_node)
    graph_builder.add_node("constraint_validation", constraint_validation_node)
    graph_builder.add_node("critic", critic_node)

    graph_builder.add_edge(START, "planner")
    graph_builder.add_edge("planner", "tool_execution")
    graph_builder.add_edge("tool_execution", "planning_state_validation")
    graph_builder.add_conditional_edges(
        "planning_state_validation",
        route_after_planning_state_validation,
        {
            "planner": "planner",
            "constraint_validation": "constraint_validation",
            "critic": "critic",
            "end": END,
        },
    )
    graph_builder.add_conditional_edges(
        "constraint_validation",
        route_after_constraint_validation,
        {
            "planner": "planner",
            "critic": "critic",
            "end": END,
        },
    )
    graph_builder.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "planner": "planner",
            "end": END,
        },
    )

    return graph_builder.compile()


planning_graph = create_planning_graph()
