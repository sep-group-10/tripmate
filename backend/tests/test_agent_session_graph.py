from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.schemas.agent_session import AgentSession, AgentSessionStatus


class PlanningState(TypedDict):
    session: AgentSession


def planning_node(state: PlanningState) -> dict:
    session = state["session"]

    session.iteration_count += 1

    return {"session": session}


def completion_node(state: PlanningState) -> dict:
    session = state["session"]

    session.status = AgentSessionStatus.COMPLETED

    return {"session": session}


def build_test_graph():
    graph_builder = StateGraph(PlanningState)

    graph_builder.add_node("planning", planning_node)
    graph_builder.add_node("completion", completion_node)

    graph_builder.add_edge(START, "planning")
    graph_builder.add_edge("planning", "completion")
    graph_builder.add_edge("completion", END)

    return graph_builder.compile()


def test_agent_session_flows_through_langgraph():
    graph = build_test_graph()

    session = AgentSession(
        user_request="Plan a 5-day trip to Kandy",
        trip_preferences={
            "destination": "Kandy",
            "duration_days": 5,
        },
    )

    result = graph.invoke({"session": session})

    updated_session = result["session"]

    assert updated_session.user_request == "Plan a 5-day trip to Kandy"
    assert updated_session.trip_preferences["destination"] == "Kandy"
    assert updated_session.iteration_count == 1
    assert updated_session.status == AgentSessionStatus.COMPLETED

def test_agent_session_supports_all_terminal_states():
    for status in AgentSessionStatus:
        session = AgentSession(
            user_request="Plan a trip to Kandy",
            status=status,
        )

        assert session.status == status