from langchain_google_genai import ChatGoogleGenerativeAI

from app.schemas.planning import PlannerDecision
from app.services.langgraph.state import PlanningState


def create_planner_model():
    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0,
    ).with_structured_output(PlannerDecision)


def planner_node(state: PlanningState) -> dict:
    session = state["session"]
    session.iteration_count += 1

    prompt = f"""
You are the TripMate planning assistant.

User request:
{session.user_request}

Trip preferences:
{session.trip_preferences}

Tool results collected so far:
{session.tool_results}

Current iteration:
{session.iteration_count}

Available tools:
- placeholder_tool: temporary tool used for testing the planning workflow.

Decide what action should happen next.

Return a structured PlannerDecision.
"""

    model = create_planner_model()
    decision = model.invoke(prompt)

    return {
        "planner_decision": decision,
    }
