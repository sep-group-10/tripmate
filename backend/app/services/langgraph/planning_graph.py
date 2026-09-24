from langgraph.graph import END, START, StateGraph

from app.services.langgraph.critic import critic_node, route_after_critic
from app.services.langgraph.planner import planner_node
from app.services.langgraph.state import PlanningState
from app.services.tools.registry import TOOLS


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

    return {
        "session": session,
        "last_failure": None,
        "consecutive_failures": 0,
    }


def create_planning_graph():
    """Build the Planner → Tool Execution → Critic planning workflow."""

    graph_builder = StateGraph(PlanningState)

    graph_builder.add_node("planner", planner_node)
    graph_builder.add_node("tool_execution", tool_execution_node)
    graph_builder.add_node("critic", critic_node)

    graph_builder.add_edge(START, "planner")
    graph_builder.add_edge("planner", "tool_execution")
    graph_builder.add_edge("tool_execution", "critic")
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
