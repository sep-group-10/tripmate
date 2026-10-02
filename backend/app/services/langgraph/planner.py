import os
from enum import Enum

from langchain_openai import ChatOpenAI
from pydantic import create_model

from app.schemas.planning import PlannerDecision
from app.services.langgraph.state import PlanningState
from app.services.langgraph.tool_inputs import runnable_tool_names
from app.services.tools.registry import TOOLS


def create_planner_model(runnable_actions: list[str]):
    """Create structured output restricted to actions usable in the current state."""

    action_enum = Enum(
        "RunnablePlannerAction",
        {name: name for name in runnable_actions},
        type=str,
    )
    decision_schema = create_model(
        "RunnablePlannerDecision",
        action=(action_enum, ...),
    )
    return ChatOpenAI(
        model="google/gemini-2.5-flash",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    ).with_structured_output(decision_schema)


def planner_node(state: PlanningState) -> dict:
    """Choose the next registered planning tool from the current session."""

    session = state["session"]
    critic_requests_replanning = bool(
        isinstance(session.critic_result, dict)
        and session.critic_result.get("continue_planning") is True
    )
    runnable_actions = runnable_tool_names(
        session,
        allow_replanning=bool(state.get("last_failure")) or critic_requests_replanning,
    )
    if not runnable_actions:
        raise RuntimeError("No planning tool is runnable from the current session")
    available_tools = "\n".join(
        f"- {name}: {TOOLS[name].description}" for name in runnable_actions
    )
    result_summaries = []
    for entry in session.tool_results:
        result = entry.get("result")
        summary = {"tool": entry.get("tool"), "result_type": type(result).__name__}
        if isinstance(result, dict):
            summary["status"] = result.get("status")
            summary["keys"] = sorted(result.keys())
            if result.get("failed_checks"):
                summary["failed_checks"] = result["failed_checks"]
                checks = result.get("checks", {})
                summary["reasons"] = [
                    reason
                    for name in result["failed_checks"]
                    for reason in checks.get(name, {}).get("reasons", [])
                ]
            days = result.get("days")
            if isinstance(days, list):
                summary["day_count"] = len(days)
            total = result.get("total")
            if isinstance(total, dict):
                summary["cost_total"] = total
        elif isinstance(result, list):
            summary["count"] = len(result)
        result_summaries.append(summary)

    prompt = f"""
You are the TripMate planning assistant.

Planning goal:
{session.goal}

Trip requirements:
{session.trip_requirements}

Current persisted itinerary (context only; do not edit or interpret this as an edit request):
{state.get("current_itinerary")}

Latest user message:
{state.get("latest_user_message")}

Tool results collected so far:
{result_summaries}

Latest Critic assessment and actionable feedback:
{session.critic_result}

Current iteration:
{session.iteration_count}

Latest planning failure, if any:
{state.get("last_failure")}

Available tools:
{available_tools}

Choose exactly one currently runnable tool by its exact name from the available tools
listed above. The structured output accepts only these runnable actions. The backend
supplies tool arguments from canonical trip requirements and stored tool results; do
not generate tool arguments. Select the next useful action from the current state.
After scheduling_engine and cost_estimator have both run, constraint_validator
is executed automatically before the Critic; do not call it manually.

Return a structured PlannerDecision.
"""

    model = create_planner_model(runnable_actions)
    raw_decision = model.invoke(prompt)
    action = raw_decision.action
    if isinstance(action, Enum):
        action = action.value

    # Keep the graph safe even when a test double or provider bypasses the schema.
    if action not in runnable_actions:
        action = runnable_actions[0]

    return {
        "planner_decision": PlannerDecision(action=action),
    }
