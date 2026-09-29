from app.schemas.agent_session import AgentSession, AgentSessionStatus
from app.services.final_response_generator import FinalResponseGenerator


def _schedule(name="Temple", *, unscheduled=None, warnings=None):
    return {
        "status": "partial" if unscheduled else "ok",
        "days": [
            {
                "day_number": 1,
                "date": "2026-10-01",
                "day_type": "day_trip",
                "items": [{"name": name, "start_time": "09:00", "end_time": "10:00"}],
            }
        ],
        "unscheduled": unscheduled or [],
        "warnings": warnings or [],
    }


def _session(status, **updates):
    values = {
        "goal": "Plan a trip to Kandy",
        "status": status,
        "tool_results": [],
    }
    values.update(updates)
    return AgentSession(**values)


def test_completed_response_summarizes_itinerary_cost_and_weather():
    session = _session(
        AgentSessionStatus.COMPLETED,
        tool_results=[
            {"tool": "scheduling_engine", "result": _schedule("Old stop")},
            {"tool": "route_optimizer", "result": _schedule("Temple")},
            {
                "tool": "cost_estimator",
                "result": {"total": {"min": 1200, "max": 1800}},
            },
            {
                "tool": "weather_validator",
                "result": {
                    "warnings": ["Weather check for 2026-10-01 returned warning"]
                },
            },
        ],
    )

    message = FinalResponseGenerator().generate(session)

    assert "2026-10-01" in message
    assert "Temple" in message
    assert "Old stop" not in message
    assert "1200–1800" in message
    assert "Weather check for 2026-10-01 returned warning" in message
    assert "tool_results" not in message


def test_completed_response_tolerates_missing_optional_data():
    message = FinalResponseGenerator().generate(_session(AgentSessionStatus.COMPLETED))

    assert "Your trip plan is ready." in message


def test_best_effort_includes_critic_feedback_and_available_plan():
    session = _session(
        AgentSessionStatus.BEST_EFFORT,
        critic_result={
            "reason": "The final day has limited activity options.",
            "suggestions": ["Add a museum visit on the final day."],
        },
        tool_results=[{"tool": "scheduling_engine", "result": _schedule("Lake walk")}],
    )

    message = FinalResponseGenerator().generate(session)

    assert "best-effort" in message
    assert "may be incomplete or imperfect" in message
    assert "Lake walk" in message
    assert "limited activity options" in message
    assert "Add a museum visit" in message
    assert "You could adjust" in message


def test_infeasible_includes_critic_constraint_and_scheduling_reasons():
    session = _session(
        AgentSessionStatus.INFEASIBLE,
        critic_result={"reason": "The event cannot fit within these trip dates."},
        constraint_result={
            "failed_constraints": ["budget", "feasibility"],
            "reasons": {
                "budget": "The maximum estimated total exceeds the trip budget."
            },
        },
        tool_results=[
            {
                "tool": "route_optimizer",
                "result": _schedule(
                    "Temple",
                    unscheduled=[
                        {
                            "name": "Festival",
                            "reason": "event's date range falls outside the trip",
                        }
                    ],
                    warnings=["no hotel candidate available for this destination"],
                ),
            }
        ],
    )

    message = FinalResponseGenerator().generate(session)

    assert "event cannot fit" in message
    assert "exceeds the trip budget" in message
    assert "Festival" in message
    assert "falls outside the trip" in message
    assert "raise the budget" in message
    assert "shift or extend the travel dates" in message


def test_failed_response_is_safe_and_friendly():
    message = FinalResponseGenerator().generate(_session(AgentSessionStatus.FAILED))

    assert "sorry" in message.lower()
    assert "couldn’t complete" in message


def test_failed_response_never_exposes_raw_technical_details():
    session = _session(
        AgentSessionStatus.FAILED,
        critic_result={"reason": "Secret provider exception"},
        tool_results=[
            {"tool": "planner", "result": {"error": "Traceback: secret traceback"}},
            {"tool": "cost_estimator", "result": {"error": "database failure"}},
        ],
    )

    message = FinalResponseGenerator().generate(session)

    assert "Secret provider exception" not in message
    assert "Traceback" not in message
    assert "secret traceback" not in message
    assert "database failure" not in message
    assert "planner" not in message
    assert "cost_estimator" not in message
