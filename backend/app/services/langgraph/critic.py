from pathlib import Path
from string import Template

from langchain_google_genai import ChatGoogleGenerativeAI

from app.schemas.agent_session import AgentSessionStatus
from app.schemas.planning import CriticDecision
from app.services.langgraph.state import PlanningState

_CRITIC_PROMPT_PATH = (
    Path(__file__).resolve().parents[2] / "agent" / "prompts" / "critic_v1.md"
)


def create_critic_model():
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0,
    ).with_structured_output(CriticDecision)


def _critic_prompt(state: PlanningState) -> str:
    session = state["session"]
    template = Template(_CRITIC_PROMPT_PATH.read_text(encoding="utf-8"))
    return template.substitute(
        goal=session.goal,
        trip_requirements=session.trip_requirements,
        tool_execution_order=session.tool_execution_order,
        tool_results=session.tool_results,
        constraint_result=session.constraint_result,
        iteration_count=session.iteration_count,
    )


def critic_node(state: PlanningState) -> dict:
    """Assess itinerary quality and persist the full structured Critic result."""

    session = state["session"]
    decision = create_critic_model().invoke(_critic_prompt(state))
    session.critic_result = decision.model_dump(mode="json")
    return {
        "session": session,
        "critic_decision": decision,
    }


def route_after_critic(state: PlanningState) -> str:
    """Decide whether to continue planning or terminate the graph."""

    session = state["session"]
    decision = state["critic_decision"]

    max_iterations = state.get("max_iterations", 8)

    if session.iteration_count >= max_iterations:
        session.status = AgentSessionStatus.BEST_EFFORT
        return "end"

    if state["consecutive_failures"] >= 2:
        session.status = AgentSessionStatus.FAILED
        return "end"

    if decision is None:
        session.status = AgentSessionStatus.FAILED
        return "end"

    if (
        not state.get("constraint_validation_current", False)
        or not session.constraint_result
        or session.constraint_result.get("status") != "pass"
    ):
        return "planner"

    weather_validated = any(
        entry.get("tool") == "weather_validator" for entry in session.tool_results
    )
    if not weather_validated:
        return "planner"

    if not decision.continue_planning:
        try:
            status = AgentSessionStatus(decision.status or "failed")
        except ValueError:
            status = AgentSessionStatus.FAILED
        session.status = status
        return "end"

    return "planner"
