from typing import NotRequired, TypedDict

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph

from app.schemas.agent_session import AgentSession, AgentSessionStatus
from app.schemas.planning import CriticDecision, PlannerDecision


class PlanningState(TypedDict):
    # Shared state that is passed between all planning nodes.
    session: AgentSession
    max_iterations: NotRequired[int]
    planner_decision: PlannerDecision | None
    critic_decision: CriticDecision | None
    last_failure: str | None
    consecutive_failures: int


@tool
def placeholder_tool() -> str:
    """Provide a temporary result until the real TripMate tools are implemented."""
    return "Placeholder tool executed successfully."


def create_planner_model():
    # Gemini is configured to return our PlannerDecision structure
    # instead of an unstructured text response.
    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0,
    ).with_structured_output(PlannerDecision)


def planner_node(state: PlanningState) -> dict:
    # Each Planner execution represents one planning iteration.
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

For this initial planning graph, the only available tool is:
placeholder_tool

Decide what action should happen next.
Return placeholder_tool when a tool action is needed.
"""

    model = create_planner_model()
    decision = model.invoke(prompt)

    # Store Gemini's decision in the shared graph state
    # so the next node can use it.
    return {
        "planner_decision": decision,
    }


def tool_execution_node(state: PlanningState) -> dict:
    # Executes the selected tool and records its result and execution order.
    session = state["session"]
    decision = state["planner_decision"]

    if decision is None:
        failure = "Planner did not provide a tool decision."

        # Count only consecutive occurrences of the same failure.
        consecutive_failures = (
            state["consecutive_failures"] + 1 if state["last_failure"] == failure else 1
        )

        return {
            "last_failure": failure,
            "consecutive_failures": consecutive_failures,
        }

    if decision.action != "placeholder_tool":
        failure = f"Unknown tool: {decision.action}"

        # A different failure starts a new consecutive-failure sequence.
        consecutive_failures = (
            state["consecutive_failures"] + 1 if state["last_failure"] == failure else 1
        )

        return {
            "last_failure": failure,
            "consecutive_failures": consecutive_failures,
        }

    result = placeholder_tool.invoke(decision.arguments)

    session.tool_results.append(
        {
            "tool": decision.action,
            "result": result,
        }
    )

    session.tool_execution_order.append(decision.action)

    return {
        "session": session,
        "last_failure": None,
        "consecutive_failures": 0,
    }


def create_critic_model():
    # Gemini evaluates the current planning state and returns
    # a structured decision for the graph.
    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0,
    ).with_structured_output(CriticDecision)


def critic_node(state: PlanningState) -> dict:
    # The Critic checks whether the current planning process
    # should continue or reach a terminal state.
    session = state["session"]

    prompt = f"""
You are the TripMate planning critic.

User request:
{session.user_request}

Trip preferences:
{session.trip_preferences}

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

    # Stop if the maximum number of iterations has been reached.
    # Use 8 iterations by default, while allowing callers to configure the limit.
    max_iterations = state.get("max_iterations", 8)

    if session.iteration_count >= max_iterations:
        session.status = AgentSessionStatus.BEST_EFFORT
        return "end"

    # Stop if repeated failures indicate that the graph is stuck.
    if state["consecutive_failures"] >= 2:
        session.status = AgentSessionStatus.FAILED
        return "end"

    if decision is None:
        session.status = AgentSessionStatus.FAILED
        return "end"

    # Gemini says the planning process is finished.
    if not decision.continue_planning:
        # Only allow the four terminal statuses defined by AgentSession.
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

    # Gemini says more planning work is required.
    return "planner"


def create_planning_graph():
    # StateGraph passes the same PlanningState through each node.
    graph_builder = StateGraph(PlanningState)

    graph_builder.add_node("planner", planner_node)
    graph_builder.add_node("tool_execution", tool_execution_node)
    graph_builder.add_node("critic", critic_node)

    # Initial flow: Planner → Tool Execution → Critic.
    graph_builder.add_edge(START, "planner")
    graph_builder.add_edge("planner", "tool_execution")
    graph_builder.add_edge("tool_execution", "critic")

    # Critic decides whether to loop back to Planner or finish.
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
