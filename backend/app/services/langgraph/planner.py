from langchain_google_genai import ChatGoogleGenerativeAI

from app.schemas.planning import PlannerDecision
from app.services.langgraph.state import PlanningState
from app.services.tools.registry import TOOLS


def create_planner_model():
    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0,
    ).with_structured_output(PlannerDecision)


def planner_node(state: PlanningState) -> dict:
    """Choose the next registered planning tool from the current session."""

    session = state["session"]
    session.iteration_count += 1
    available_tools = "\n".join(
        f"- {name}: {tool.description}" for name, tool in TOOLS.items()
    )

    prompt = f"""
You are the TripMate planning assistant.

Planning goal:
{session.goal}

Trip requirements:
{session.trip_requirements}

Tool results collected so far:
{session.tool_results}

Current iteration:
{session.iteration_count}

Available tools:
{available_tools}

Decide what action should happen next.

Return a structured PlannerDecision.
"""

    model = create_planner_model()
    decision = model.invoke(prompt)

    return {
        "planner_decision": decision,
    }
