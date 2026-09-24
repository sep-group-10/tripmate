from app.schemas.agent_session import AgentSession, AgentSessionStatus


def test_agent_session_has_required_fields():
    session = AgentSession(
        goal="Plan a 5-day trip to Kandy",
        trip_requirements={
            "destination": "Kandy",
            "duration_days": 5,
            "budget": "medium",
        },
    )

    assert session.goal == "Plan a 5-day trip to Kandy"
    assert session.trip_requirements["destination"] == "Kandy"

    assert session.candidates == []
    assert session.ranked_candidates == []
    assert session.itinerary is None
    assert session.optimised_route is None
    assert session.constraint_result is None

    assert session.tool_results == []
    assert session.tool_execution_order == []
    assert session.iteration_count == 0
    assert session.status is None


def test_agent_session_stores_tool_results():
    session = AgentSession(
        goal="Find attractions in Kandy",
        tool_results=[
            {
                "tool": "search_attractions",
                "result": ["Temple of the Tooth"],
            }
        ],
    )

    assert len(session.tool_results) == 1
    assert session.tool_results[0]["tool"] == "search_attractions"


def test_agent_session_status_values():
    assert AgentSessionStatus.COMPLETED.value == "completed"
    assert AgentSessionStatus.BEST_EFFORT.value == "best_effort"
    assert AgentSessionStatus.INFEASIBLE.value == "infeasible"
    assert AgentSessionStatus.FAILED.value == "failed"


def test_agent_session_can_be_updated():
    session = AgentSession(
        goal="Plan a trip to Kandy",
    )

    session.iteration_count += 1
    session.status = AgentSessionStatus.COMPLETED
    session.tool_results.append(
        {
            "tool": "search_attractions",
            "result": ["Temple of the Tooth"],
        }
    )

    assert session.iteration_count == 1
    assert session.status == AgentSessionStatus.COMPLETED
    assert len(session.tool_results) == 1


def test_agent_session_stores_tool_execution_order():
    session = AgentSession(
        goal="Plan a trip to Kandy",
        tool_execution_order=[
            "preference_processor",
            "candidate_retriever",
            "scoring_engine",
        ],
    )

    assert session.tool_execution_order == [
        "preference_processor",
        "candidate_retriever",
        "scoring_engine",
    ]
