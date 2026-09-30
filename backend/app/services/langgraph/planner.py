import json
import os

from langchain_openai import ChatOpenAI

from app.schemas.planning import PlannerDecision
from app.services.langgraph.state import PlanningState
from app.services.tools.registry import TOOLS


def create_planner_model():
    return ChatOpenAI(
        model="google/gemini-2.5-flash",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    ).with_structured_output(PlannerDecision)


def planner_node(state: PlanningState) -> dict:
    """Choose the next registered planning tool from the current session."""

    session = state["session"]
    session.iteration_count += 1
    available_tools = "\n".join(
        f"- {name} arguments={json.dumps(tool.args, sort_keys=True)}: {tool.description}"
        for name, tool in TOOLS.items()
    )

    prompt = f"""
You are the TripMate planning assistant.

Planning goal:
{session.goal}

Trip requirements:
{session.trip_requirements}

Tool results collected so far:
{session.tool_results}

Latest Critic assessment and actionable feedback:
{session.critic_result}

Current iteration:
{session.iteration_count}

Available tools:
{available_tools}

Decide what action should happen next based on the current session and collected results.
Choose one registered tool by its exact name. Set arguments to an object matching
that tool's argument schema, using trip requirements and prior tool results as inputs.
Do not assume a fixed tool order; select the next useful action from the current state.
When calling weather_validator, pass the schedule dictionary from the most recent
scheduling_engine result in session.tool_results as its schedule argument.
After scheduling_engine and cost_estimator have both run, constraint_validator
is executed automatically before the Critic; do not call it manually.

Return a structured PlannerDecision.
"""

    model = create_planner_model()
    decision = model.invoke(prompt)

    return {
        "planner_decision": decision,
    }
