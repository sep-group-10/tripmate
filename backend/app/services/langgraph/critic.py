from langchain_google_genai import ChatGoogleGenerativeAI

from app.schemas.agent_session import AgentSessionStatus
from app.schemas.planning import CriticDecision
from app.services.langgraph.state import PlanningState


def create_critic_model():
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0,
    ).with_structured_output(CriticDecision)


def critic_node(state: PlanningState) -> dict:
    session = state["session"]

    prompt = f"""
You are the TripMate planning critic.

Planning goal:
{session.goal}

Trip requirements:
{session.trip_requirements}

Tool execution order:
{session.tool_execution_order}

Tool results:
{session.tool_results}

Current iteration:
{session.iteration_count}

Evaluate the current planning progress.

If the available information is sufficient, finish the planning process.

Use one of these terminal statuses:
completed
best_effort
infeasible
failed

If more planning work is required, continue planning.

Return a structured CriticDecision.
"""

    model = create_critic_model()
    decision = model.invoke(prompt)

    return {
        "critic_decision": decision,
    }


def route_after_critic(state: PlanningState) -> str:
    """Decide whether the graph should continue or terminate."""

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

    if not decision.continue_planning:
        valid_statuses = {
            AgentSessionStatus.COMPLETED,
            AgentSessionStatus.BEST_EFFORT,
            AgentSessionStatus.INFEASIBLE,
            AgentSessionStatus.FAILED,
        }

        try:
            status = AgentSessionStatus(decision.status or "failed")
        except ValueError:
            status = AgentSessionStatus.FAILED

        if status not in valid_statuses:
            status = AgentSessionStatus.FAILED

        session.status = status
        return "end"

    return "planner"
