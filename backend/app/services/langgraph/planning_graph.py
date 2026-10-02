from fastapi.encoders import jsonable_encoder
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from sqlalchemy.orm import Session

from app.models.agent_execution_trace import AgentExecutionTrace
from app.schemas.agent_session import AgentSessionStatus
from app.services.langgraph.context import PlanningContext
from app.services.langgraph.critic import critic_node, route_after_critic
from app.services.langgraph.planner import planner_node
from app.services.langgraph.state import PlanningState
from app.services.langgraph.state_validator import (
    is_valid_constraint_result,
    is_valid_tool_result,
    validate_planning_state,
)
from app.services.langgraph.tool_inputs import (
    _assemble_tool_input,
    _latest_tool_result,
)
from app.services.tools.registry import TOOLS

_PLANNING_STATE_VALIDATION_FAILURE = "Planning state validation failed."
_CONSTRAINT_VALIDATION_FAILURE = "Constraint validation failed."
_PRE_CRITIC_STALL_FAILURE = (
    "Pre-Critic planning repeated a tool without passing constraints."
)
_MISSING_TOOL_INPUT_FAILURE = "Missing canonical input for selected tool"


def _add_tool_trace(
    runtime: Runtime[PlanningContext] | None,
    *,
    session,
    tool_name: str,
    tool_input: dict,
    tool_output,
    success: bool,
) -> None:
    """Add an execution trace to the request transaction when context exists."""

    if runtime is None or runtime.context is None:
        return

    context = runtime.context
    db: Session = context["db"]
    db.add(
        AgentExecutionTrace(
            planning_session_id=context["planning_session_id"],
            tool_name=tool_name,
            tool_input=jsonable_encoder(tool_input),
            tool_output=jsonable_encoder(tool_output),
            success=success,
            iteration_number=session.iteration_count,
        )
    )


def tool_execution_node(
    state: PlanningState,
    runtime: Runtime[PlanningContext] | None = None,
) -> dict:
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

    tool_input = _assemble_tool_input(session, decision.action)
    if tool_input is None:
        failure = f"{_MISSING_TOOL_INPUT_FAILURE}: {decision.action}"
        consecutive_failures = (
            state["consecutive_failures"] + 1 if state["last_failure"] == failure else 1
        )
        return {
            "last_failure": failure,
            "consecutive_failures": consecutive_failures,
        }

    previous_tool_name = (
        session.tool_execution_order[-1] if session.tool_execution_order else None
    )
    try:
        result = tool.invoke(tool_input)
    except Exception as exc:
        _add_tool_trace(
            runtime,
            session=session,
            tool_name=decision.action,
            tool_input=tool_input,
            tool_output={"error_type": type(exc).__name__, "error": str(exc)},
            success=False,
        )
        raise

    _add_tool_trace(
        runtime,
        session=session,
        tool_name=decision.action,
        tool_input=tool_input,
        tool_output=result,
        success=True,
    )
    session.tool_results.append(
        {
            "tool": decision.action,
            "result": result,
        }
    )
    session.tool_execution_order.append(decision.action)
    tool_result_is_valid = is_valid_tool_result(decision.action, result)
    structural_failure_is_pending = (
        state["last_failure"] == _PLANNING_STATE_VALIDATION_FAILURE
    )
    repeated_tool_selection = previous_tool_name == decision.action
    preserve_structural_failure = structural_failure_is_pending and (
        not tool_result_is_valid or repeated_tool_selection
    )
    preserve_constraint_failure = state["last_failure"] in {
        _CONSTRAINT_VALIDATION_FAILURE,
        _PRE_CRITIC_STALL_FAILURE,
    }
    preserve_failure = preserve_structural_failure or preserve_constraint_failure
    state_update = {
        "session": session,
        "last_failure": state["last_failure"] if preserve_failure else None,
        "consecutive_failures": state["consecutive_failures"]
        if preserve_failure
        else 0,
    }
    if decision.action in {"scheduling_engine", "route_optimizer", "cost_estimator"}:
        session.constraint_result = None
        state_update["constraint_validation_current"] = False
    elif decision.action == "constraint_validator":
        session.constraint_result = result
        state_update["constraint_validation_current"] = is_valid_constraint_result(
            result
        )

    return {
        **state_update,
    }


def planning_state_validation_node(state: PlanningState) -> dict:
    """Check the current session structure after each Planner-selected tool."""

    session = state["session"]
    result = validate_planning_state(session)
    session.tool_results.append({"tool": "planning_state_validator", "result": result})
    if result.get("status") != "pass":
        if (state["last_failure"] or "").startswith(_MISSING_TOOL_INPUT_FAILURE):
            return {"session": session}
        consecutive_failures = (
            state["consecutive_failures"] + 1
            if state["last_failure"] == _PLANNING_STATE_VALIDATION_FAILURE
            else 1
        )
        return {
            "session": session,
            "last_failure": _PLANNING_STATE_VALIDATION_FAILURE,
            "consecutive_failures": consecutive_failures,
        }

    if state["last_failure"] == _PLANNING_STATE_VALIDATION_FAILURE:
        return {"session": session, "last_failure": None, "consecutive_failures": 0}

    if (state["last_failure"] or "").startswith(_MISSING_TOOL_INPUT_FAILURE):
        return {"session": session}

    next_route = route_after_tool_execution(state)
    constraint_result = session.constraint_result
    constraint_validation_is_current = state.get("constraint_validation_current", False)
    constraints_are_passing = (
        constraint_validation_is_current
        and constraint_result is not None
        and constraint_result.get("status") == "pass"
    )
    if next_route != "constraint_validation" and not constraints_are_passing:
        if constraint_result is not None:
            failure = _CONSTRAINT_VALIDATION_FAILURE
        else:
            execution_order = session.tool_execution_order
            decision = state["planner_decision"]
            repeated_tool = (
                decision is not None
                and len(execution_order) > 1
                and execution_order[-1] == decision.action
                and execution_order[-2] == decision.action
            )
            if not repeated_tool:
                if state["last_failure"] == _PRE_CRITIC_STALL_FAILURE:
                    return {
                        "session": session,
                        "last_failure": None,
                        "consecutive_failures": 0,
                    }
                return {"session": session}
            failure = _PRE_CRITIC_STALL_FAILURE

        consecutive_failures = (
            state["consecutive_failures"] + 1 if state["last_failure"] == failure else 1
        )
        return {
            "session": session,
            "last_failure": failure,
            "consecutive_failures": consecutive_failures,
        }
    return {"session": session}


def route_after_planning_state_validation(state: PlanningState) -> str:
    """Replan invalid sessions, preserving graph termination guards."""

    session = state["session"]
    result = _latest_tool_result(session, "planning_state_validator") or {}
    if result.get("status") != "pass":
        if state["consecutive_failures"] >= 2:
            session.status = AgentSessionStatus.FAILED
            return "end"
        return "planner"

    if (state["last_failure"] or "").startswith(_MISSING_TOOL_INPUT_FAILURE):
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

    if state["consecutive_failures"] >= 2:
        session.status = AgentSessionStatus.FAILED
        return "end"
    return "planner"


def constraint_validation_node(
    state: PlanningState,
    runtime: Runtime[PlanningContext] | None = None,
) -> dict:
    """Validate constraints once scheduling and cost results are available."""

    session = state["session"]
    itinerary = _latest_tool_result(session, "route_optimizer")
    if itinerary is None:
        itinerary = _latest_tool_result(session, "scheduling_engine")
    cost_estimate = _latest_tool_result(session, "cost_estimator")
    tool_input = {
        "itinerary": itinerary,
        "trip_requirements": session.trip_requirements,
        "cost_estimate": cost_estimate,
    }
    try:
        result = TOOLS["constraint_validator"].invoke(tool_input)
    except Exception as exc:
        _add_tool_trace(
            runtime,
            session=session,
            tool_name="constraint_validator",
            tool_input=tool_input,
            tool_output={"error_type": type(exc).__name__, "error": str(exc)},
            success=False,
        )
        raise

    _add_tool_trace(
        runtime,
        session=session,
        tool_name="constraint_validator",
        tool_input=tool_input,
        tool_output=result,
        success=True,
    )
    session.constraint_result = result
    session.tool_results.append({"tool": "constraint_validator", "result": result})
    session.tool_execution_order.append("constraint_validator")
    if result.get("status") == "pass":
        if state.get("last_failure") in {
            _CONSTRAINT_VALIDATION_FAILURE,
            _PRE_CRITIC_STALL_FAILURE,
        }:
            return {
                "session": session,
                "constraint_validation_current": True,
                "last_failure": None,
                "consecutive_failures": 0,
            }
        return {"session": session, "constraint_validation_current": True}

    consecutive_failures = (
        state["consecutive_failures"] + 1
        if state["last_failure"] == _CONSTRAINT_VALIDATION_FAILURE
        else 1
    )
    return {
        "session": session,
        "constraint_validation_current": True,
        "last_failure": _CONSTRAINT_VALIDATION_FAILURE,
        "consecutive_failures": consecutive_failures,
    }


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

    if state["consecutive_failures"] >= 2:
        session.status = AgentSessionStatus.FAILED
        return "end"

    return "planner"


def critic_continuation_planner_node(state: PlanningState) -> dict:
    """Count a Planner call reached through the Critic continuation edge."""

    state["session"].iteration_count += 1
    return planner_node(state)


def create_planning_graph():
    """Build the Planner → Tool Execution → Critic planning workflow."""

    graph_builder = StateGraph(PlanningState, context_schema=PlanningContext)

    graph_builder.add_node("planner", planner_node)
    graph_builder.add_node(
        "critic_continuation_planner", critic_continuation_planner_node
    )
    graph_builder.add_node("tool_execution", tool_execution_node)
    graph_builder.add_node("planning_state_validation", planning_state_validation_node)
    graph_builder.add_node("constraint_validation", constraint_validation_node)
    graph_builder.add_node("critic", critic_node)

    graph_builder.add_edge(START, "planner")
    graph_builder.add_conditional_edges(
        "planner",
        lambda state: "end"
        if state.get("planner_decision")
        and state["planner_decision"].edit_plan
        and state["planner_decision"].edit_plan.operation == "remove"
        else "tool_execution",
        {"end": END, "tool_execution": "tool_execution"},
    )
    graph_builder.add_edge("critic_continuation_planner", "tool_execution")
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
            "planner": "critic_continuation_planner",
            "end": END,
        },
    )

    return graph_builder.compile()


planning_graph = create_planning_graph()
