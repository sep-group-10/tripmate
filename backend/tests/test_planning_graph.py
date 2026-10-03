import inspect

import pytest

from app.schemas.agent_session import AgentSession, AgentSessionStatus
from app.schemas.planning import CriticDecision, ItineraryEditPlan, PlannerDecision
from app.services.langgraph import critic, planner
from app.services.langgraph.planning_graph import (
    planning_graph,
    planning_state_validation_node,
    route_after_constraint_validation,
    route_after_critic,
    route_after_planning_state_validation,
    tool_execution_node,
)


def make_critic_decision(**kwargs):
    assessment = {"score": 3, "reasoning": "The plan has a reasonable structure."}
    return CriticDecision(
        **kwargs,
        variety=assessment,
        daily_balance=assessment,
        interest_match=assessment,
        pacing=assessment,
    )


def create_state(
    *,
    iteration_count=1,
    max_iterations=8,
    continue_planning=True,
    status=None,
    consecutive_failures=0,
):
    """Create a small fake graph state for testing routing."""
    session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy"},
        iteration_count=iteration_count,
        constraint_result={"status": "pass"},
        tool_results=[{"tool": "weather_validator", "result": {"status": "ok"}}],
    )

    decision = make_critic_decision(
        continue_planning=continue_planning,
        status=status,
    )

    return {
        "session": session,
        "max_iterations": max_iterations,
        "planner_decision": None,
        "critic_decision": decision,
        "last_failure": None,
        "consecutive_failures": consecutive_failures,
        "constraint_validation_current": True,
    }


def _assert_constraint_validator_itinerary(monkeypatch, tool_results, expected):
    from langchain_core.tools import tool

    from app.services.langgraph.planning_graph import constraint_validation_node
    from app.services.tools import registry

    calls = []

    @tool
    def constraint_validator(
        itinerary: dict, trip_requirements: dict, cost_estimate: dict
    ) -> dict:
        """Record the automatic validator's effective itinerary."""
        calls.append((itinerary, trip_requirements, cost_estimate))
        return {
            "status": "pass",
            "passed": True,
            "constraints": {},
            "failed_constraints": [],
            "reasons": {},
        }

    monkeypatch.setitem(registry.TOOLS, "constraint_validator", constraint_validator)
    session = AgentSession(
        goal="Plan a trip",
        trip_requirements={"destination": "Kandy"},
        tool_results=tool_results,
    )

    constraint_validation_node({"session": session})

    assert calls == [
        (
            expected,
            {"destination": "Kandy"},
            {"total": {"min": 10, "max": 20}},
        )
    ]


def test_constraint_validator_uses_route_optimizer_output(monkeypatch):
    scheduled = {"status": "ok", "days": [{"items": [{"name": "Raw order"}]}]}
    optimized = {"status": "ok", "days": [{"items": [{"name": "Final order"}]}]}
    _assert_constraint_validator_itinerary(
        monkeypatch,
        [
            {"tool": "scheduling_engine", "result": scheduled},
            {"tool": "route_optimizer", "result": optimized},
            {"tool": "cost_estimator", "result": {"total": {"min": 10, "max": 20}}},
        ],
        optimized,
    )


def test_constraint_validator_falls_back_to_scheduling_engine_output(monkeypatch):
    scheduled = {"status": "ok", "days": [{"items": [{"name": "Scheduled order"}]}]}
    _assert_constraint_validator_itinerary(
        monkeypatch,
        [
            {"tool": "scheduling_engine", "result": scheduled},
            {"tool": "cost_estimator", "result": {"total": {"min": 10, "max": 20}}},
        ],
        scheduled,
    )


def test_planning_state_validation_routes_invalid_session_to_planner():
    state = create_state()
    result = {"status": "fail", "failed_checks": ["itinerary"]}
    state["session"].tool_results.append(
        {"tool": "planning_state_validator", "result": result}
    )

    assert route_after_planning_state_validation(state) == "planner"
    assert state["session"].tool_results[-1]["result"] == result


def test_first_structural_validation_failure_increments_counter():
    state = create_state()

    result = planning_state_validation_node(state)

    assert result["consecutive_failures"] == 1
    assert result["last_failure"] == "Planning state validation failed."


def test_second_consecutive_structural_failure_uses_failed_termination(
    monkeypatch,
):
    from langchain_core.tools import tool

    from app.services.tools import registry

    @tool
    def candidate_retriever(destination: str) -> list[dict]:
        """Return candidates while leaving the invalid session incomplete."""
        return [{"category": "attraction", "name": "Lake walk"}]

    monkeypatch.setitem(registry.TOOLS, "candidate_retriever", candidate_retriever)
    state = create_state()
    first_validation = planning_state_validation_node(state)
    state.update(first_validation)
    state["planner_decision"] = PlannerDecision(
        action="candidate_retriever", arguments={"destination": "Kandy"}
    )

    execution = tool_execution_node(state)
    state.update(execution)
    second_validation = planning_state_validation_node(state)
    state.update(second_validation)

    assert state["consecutive_failures"] == 2
    assert route_after_planning_state_validation(state) == "end"
    assert state["session"].status == AgentSessionStatus.FAILED


def test_successful_structural_validation_resets_failure_sequence(monkeypatch):
    from app.services.langgraph import planning_graph as graph_module

    validation_results = iter(
        [
            {"status": "fail", "failed_checks": ["itinerary"]},
            {"status": "pass", "failed_checks": []},
            {"status": "fail", "failed_checks": ["itinerary"]},
        ]
    )
    monkeypatch.setattr(
        graph_module,
        "validate_planning_state",
        lambda _session: next(validation_results),
    )
    state = create_state()
    state.update(planning_state_validation_node(state))
    assert state["consecutive_failures"] == 1

    state.update(planning_state_validation_node(state))

    assert state["consecutive_failures"] == 0
    assert state["last_failure"] is None

    state.update(planning_state_validation_node(state))
    assert state["consecutive_failures"] == 1


def test_planning_state_validation_does_not_apply_iteration_guard():
    state = create_state(iteration_count=8, max_iterations=8)
    state["session"].tool_results.append(
        {"tool": "planning_state_validator", "result": {"status": "fail"}}
    )

    assert route_after_planning_state_validation(state) == "planner"
    assert state["session"].status is None


def test_planning_state_validation_preserves_repeated_failure_guard():
    state = create_state(consecutive_failures=2)
    state["session"].tool_results.append(
        {"tool": "planning_state_validator", "result": {"status": "fail"}}
    )

    assert route_after_planning_state_validation(state) == "end"
    assert state["session"].status == AgentSessionStatus.FAILED


def test_valid_planning_state_uses_existing_tool_route():
    state = create_state()
    state["session"].tool_results.extend(
        [
            {"tool": "scheduling_engine", "result": {"status": "ok"}},
            {"tool": "cost_estimator", "result": {"total": {"max": 10}}},
            {"tool": "planning_state_validator", "result": {"status": "pass"}},
        ]
    )
    state["session"].constraint_result = None
    state["planner_decision"] = PlannerDecision(action="cost_estimator", arguments={})

    assert route_after_planning_state_validation(state) == "constraint_validation"

    state["planner_decision"] = PlannerDecision(action="route_optimizer", arguments={})
    assert route_after_planning_state_validation(state) == "planner"


def test_failed_constraint_validation_routes_to_planner_and_preserves_result():
    state = create_state()
    constraint_result = {
        "status": "fail",
        "failed_constraints": ["budget"],
        "reasons": {"budget": "Maximum estimated total exceeds the trip budget."},
    }
    state["session"].constraint_result = constraint_result
    state["session"].tool_results.append(
        {"tool": "constraint_validator", "result": constraint_result}
    )

    result = route_after_constraint_validation(state)

    assert result == "planner"
    assert state["session"].constraint_result == constraint_result
    assert state["session"].tool_results[-1]["result"] == constraint_result


def test_failed_constraint_validation_does_not_apply_iteration_guard():
    state = create_state(iteration_count=8, max_iterations=8)
    state["session"].constraint_result = {"status": "fail"}

    assert route_after_constraint_validation(state) == "planner"
    assert state["session"].status is None


def test_failed_constraint_validation_respects_repeated_failure_guard():
    state = create_state(consecutive_failures=2)
    state["session"].constraint_result = {"status": "fail"}

    assert route_after_constraint_validation(state) == "end"
    assert state["session"].status == AgentSessionStatus.FAILED


def test_passing_constraint_validation_routes_to_critic():
    state = create_state()
    state["session"].constraint_result = {
        "status": "pass",
        "failed_constraints": [],
        "reasons": {},
    }
    state["constraint_validation_current"] = True

    assert route_after_constraint_validation(state) == "critic"


def test_critic_can_finish_after_successful_constraints():
    state = create_state(continue_planning=True)

    result = route_after_critic(state)

    assert result == "end"
    assert state["session"].status == AgentSessionStatus.COMPLETED


def test_critic_can_finish_with_completed_status():
    state = create_state(
        continue_planning=False,
        status="completed",
    )
    result = route_after_critic(state)

    assert result == "end"
    assert state["session"].status == AgentSessionStatus.COMPLETED


def test_critic_can_finish_without_weather_validation_when_constraints_pass():
    state = create_state(
        continue_planning=False,
        status="completed",
    )
    state["session"].tool_results.clear()

    result = route_after_critic(state)

    assert result == "end"
    assert state["session"].status == AgentSessionStatus.COMPLETED


def test_graph_stops_at_maximum_iterations():
    state = create_state(
        iteration_count=8,
        max_iterations=8,
        continue_planning=True,
    )

    result = route_after_critic(state)

    assert result == "end"
    assert state["session"].status == AgentSessionStatus.BEST_EFFORT


def test_graph_stops_after_repeated_failures():
    state = create_state(
        consecutive_failures=2,
        continue_planning=True,
    )

    result = route_after_critic(state)

    assert result == "end"
    assert state["session"].status == AgentSessionStatus.FAILED


def test_critic_can_finish_with_infeasible_status():
    state = create_state(
        continue_planning=False,
        status="infeasible",
    )
    result = route_after_critic(state)

    assert result == "end"
    assert state["session"].status == AgentSessionStatus.INFEASIBLE


def test_graph_uses_default_max_iterations():
    state = create_state(
        iteration_count=8,
        continue_planning=True,
    )

    # Remove the value to verify that the graph uses its default of 8.
    state.pop("max_iterations")

    result = route_after_critic(state)

    assert result == "end"
    assert state["session"].status == AgentSessionStatus.BEST_EFFORT


def test_planning_graph_flow(monkeypatch):
    """Valid state continues through existing Critic weather gating."""
    from langchain_core.tools import tool

    from app.services.tools import registry

    schedule = {
        "status": "ok",
        "days": [
            {
                "day_number": 1,
                "date": "2026-10-05",
                "day_type": "day_trip",
                "items": [
                    {
                        "candidate_id": "place-1",
                        "category": "attraction",
                        "name": "Temple of the Tooth",
                        "start_time": "09:00",
                        "end_time": "10:00",
                        "latitude": 7.29,
                        "longitude": 80.63,
                        "duration_minutes": 60,
                        "opening_hours": None,
                    }
                ],
                "hotel_id": None,
                "hotel_location": None,
                "warnings": [],
            }
        ],
        "hotel_by_destination": {},
        "unscheduled": [],
        "warnings": [],
    }

    @tool
    def scheduling_engine(candidates: list[dict], trip_requirements: dict) -> dict:
        """Return a usable schedule without external calls."""
        return schedule

    @tool
    def cost_estimator(
        itinerary: dict, candidates: list[dict], trip_requirements: dict
    ) -> dict:
        """Return a local deterministic estimate for the graph test."""
        categories = (
            "transport_intercity",
            "transport_local",
            "accommodation",
            "activities",
            "dining",
            "miscellaneous",
            "total",
        )
        return {
            **{category: {"min": 100, "max": 200} for category in categories},
            "travellers": 2,
            "warnings": [],
        }

    @tool
    def weather_validator(schedule: dict) -> dict:
        """Stub the weather check without calling OpenWeather."""
        return {"status": "ok", "days": [], "warnings": []}

    monkeypatch.setitem(registry.TOOLS, "scheduling_engine", scheduling_engine)
    monkeypatch.setitem(registry.TOOLS, "cost_estimator", cost_estimator)
    monkeypatch.setitem(registry.TOOLS, "weather_validator", weather_validator)
    decisions = [
        PlannerDecision(
            action="scheduling_engine",
            arguments={"candidates": [], "trip_requirements": {}},
        ),
        PlannerDecision(
            action="weather_validator",
            arguments={"schedule": schedule},
        ),
        PlannerDecision(
            action="cost_estimator",
            arguments={
                "itinerary": schedule,
                "candidates": [],
                "trip_requirements": {},
            },
        ),
    ]

    class FakePlannerModel:
        def __init__(self):
            self.calls = 0

        def invoke(self, _prompt):
            decision = decisions[self.calls]
            self.calls += 1
            return decision

    class FakeCriticModel:
        def __init__(self):
            self.calls = 0

        def invoke(self, _prompt):
            self.calls += 1
            return make_critic_decision(continue_planning=False, status="completed")

    planner_model = FakePlannerModel()
    critic_model = FakeCriticModel()
    monkeypatch.setattr(
        planner, "create_planner_model", lambda _runnable_actions: planner_model
    )
    monkeypatch.setattr(critic, "create_critic_model", lambda: critic_model)

    session = AgentSession(
        goal="Plan a simple one-day trip to Kandy.",
        trip_requirements={
            "destination": "Kandy",
            "start_date": "2026-10-05",
            "end_date": "2026-10-05",
            "budget": 50000,
            "travelers": 2,
        },
        tool_results=[
            {"tool": "candidate_retriever", "result": []},
            {"tool": "scoring_engine", "result": []},
        ],
    )

    session.tool_execution_order = ["candidate_retriever", "scoring_engine"]
    result = planning_graph.invoke(
        {
            "session": session,
            "max_iterations": 8,
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }
    )

    assert result["session"].status == AgentSessionStatus.COMPLETED
    assert result["session"].tool_execution_order == [
        "candidate_retriever",
        "scoring_engine",
        "scheduling_engine",
        "weather_validator",
        "cost_estimator",
        "constraint_validator",
    ]
    assert [entry["tool"] for entry in result["session"].tool_results] == [
        "candidate_retriever",
        "scoring_engine",
        "scheduling_engine",
        "planning_state_validator",
        "weather_validator",
        "planning_state_validator",
        "cost_estimator",
        "planning_state_validator",
        "constraint_validator",
    ]
    assert all(
        entry["result"]["status"] == "pass"
        for entry in result["session"].tool_results
        if entry["tool"] == "planning_state_validator"
    )
    assert planner_model.calls == 3
    assert critic_model.calls == 1


def test_invalid_state_exposes_only_scoring_action_after_candidate_result(
    monkeypatch,
):
    class FakePlannerModel:
        def __init__(self):
            self.actions = None
            self.prompt = None

        def invoke(self, prompt):
            self.prompt = prompt
            return PlannerDecision(action="scoring_engine")

    model = FakePlannerModel()
    captured_actions = []

    def model_factory(runnable_actions):
        captured_actions.extend(runnable_actions)
        return model

    monkeypatch.setattr(planner, "create_planner_model", model_factory)
    session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={
            "destination": "Kandy",
            "start_date": "2026-10-05",
            "end_date": "2026-10-05",
            "budget": 50000,
            "travelers": 2,
        },
        tool_results=[
            {
                "tool": "candidate_retriever",
                "result": [{"id": "place-1", "category": "attraction", "name": "Lake"}],
            },
            {
                "tool": "planning_state_validator",
                "result": {
                    "status": "fail",
                    "passed": False,
                    "failed_checks": ["itinerary"],
                    "checks": {
                        "itinerary": {
                            "reasons": [
                                "A scheduling_engine result is missing or is not an object."
                            ]
                        }
                    },
                },
            },
        ],
    )
    state = {
        "session": session,
        "planner_decision": None,
        "critic_decision": None,
        "last_failure": "Planning state validation failed.",
        "consecutive_failures": 1,
    }

    result = planner.planner_node(state)

    assert captured_actions == ["scoring_engine"]
    assert "scheduling_engine:" not in model.prompt
    assert result["planner_decision"].action == "scoring_engine"


def test_real_planner_uses_current_agent_session_fields(monkeypatch):
    class FakeModel:
        def __init__(self):
            self.prompts = []

        def invoke(self, prompt):
            self.prompts.append(prompt)
            return PlannerDecision(
                action="candidate_retriever", arguments={"destination": "Planner value"}
            )

    model = FakeModel()
    monkeypatch.setattr(
        planner, "create_planner_model", lambda _runnable_actions: model
    )
    session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy", "duration_days": 3},
    )

    result = planner.planner_node(
        {
            "session": session,
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }
    )

    assert result["planner_decision"].action == "candidate_retriever"
    assert session.iteration_count == 0
    assert "Plan a trip to Kandy" in model.prompts[0]
    assert "'destination': 'Kandy'" in model.prompts[0]


def test_planner_decision_schema_is_compact_and_action_is_constrained():
    import pytest
    from pydantic import ValidationError

    decision = PlannerDecision(action="candidate_retriever")
    assert decision.model_dump() == {
        "action": "candidate_retriever",
        "edit_plan": None,
    }
    assert set(PlannerDecision.model_json_schema()["properties"]) == {
        "action",
        "edit_plan",
    }
    with pytest.raises(ValidationError):
        PlannerDecision(action="not_a_registered_tool")


def test_planner_prompt_summarizes_large_tool_results(monkeypatch):
    class FakeModel:
        def invoke(self, prompt):
            self.prompt = prompt
            return PlannerDecision(action="scoring_engine")

    model = FakeModel()
    monkeypatch.setattr(
        planner, "create_planner_model", lambda _runnable_actions: model
    )
    large_payload = "UNIQUE_LARGE_SCHEDULE_PAYLOAD" * 500
    session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy"},
        tool_results=[
            {"tool": "candidate_retriever", "result": [{"name": large_payload}]}
        ],
    )

    planner.planner_node(
        {
            "session": session,
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }
    )

    assert "UNIQUE_LARGE_SCHEDULE_PAYLOAD" not in model.prompt
    assert "candidate_retriever" in model.prompt
    assert "count" in model.prompt
    assert "supplies tool arguments" in model.prompt.lower()


def test_real_critic_uses_current_agent_session_fields(monkeypatch):
    class FakeModel:
        def __init__(self):
            self.prompts = []

        def invoke(self, prompt):
            self.prompts.append(prompt)
            return make_critic_decision(continue_planning=False, status="completed")

    model = FakeModel()
    monkeypatch.setattr(critic, "create_critic_model", lambda: model)
    session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy", "duration_days": 3},
        constraint_result={"status": "pass"},
    )

    result = critic.critic_node(
        {
            "session": session,
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }
    )

    assert result["critic_decision"].status == "completed"
    assert session.critic_result == result["critic_decision"].model_dump(mode="json")
    assert "Plan a trip to Kandy" in model.prompts[0]
    assert "'destination': 'Kandy'" in model.prompts[0]


def test_planning_components_do_not_reference_removed_session_fields():
    for component in (planner, critic):
        source = inspect.getsource(component)
        assert "session.user_request" not in source
        assert "session.trip_preferences" not in source


def test_different_failures_reset_consecutive_failure_count(monkeypatch):
    """Different failures must not be treated as a deadlock."""

    state = create_state(
        consecutive_failures=1,
        continue_planning=True,
    )

    from app.services.tools import registry

    monkeypatch.delitem(registry.TOOLS, "candidate_retriever")
    state["last_failure"] = "Unknown tool: first_tool"
    state["planner_decision"] = PlannerDecision(action="candidate_retriever")

    result = tool_execution_node(state)

    assert result["last_failure"] == "Unknown tool: candidate_retriever"
    assert result["consecutive_failures"] == 1


def test_same_failure_increments_consecutive_failure_count(monkeypatch):
    """The same failure must increase the deadlock counter."""

    state = create_state(
        consecutive_failures=1,
        continue_planning=True,
    )

    from app.services.tools import registry

    monkeypatch.delitem(registry.TOOLS, "candidate_retriever")
    failure = "Unknown tool: candidate_retriever"
    state["last_failure"] = failure
    state["planner_decision"] = PlannerDecision(action="candidate_retriever")

    result = tool_execution_node(state)

    assert result["last_failure"] == failure
    assert result["consecutive_failures"] == 2


def test_constraint_validator_is_not_a_planner_action_when_automatic_inputs_exist():
    from app.services.langgraph.tool_inputs import runnable_tool_names

    session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy"},
        tool_results=[
            {"tool": "candidate_retriever", "result": []},
            {"tool": "scoring_engine", "result": []},
            {"tool": "scheduling_engine", "result": {"status": "ok", "days": []}},
            {"tool": "cost_estimator", "result": {"total": {"min": 0, "max": 0}}},
        ],
    )

    assert "constraint_validator" not in runnable_tool_names(session)


def test_successful_scheduling_stage_is_not_runnable_again_without_replanning():
    from app.services.langgraph.tool_inputs import runnable_tool_names

    schedule = {"status": "ok", "days": [{"items": []}]}
    session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy"},
        tool_results=[
            {"tool": "candidate_retriever", "result": [{"id": "place-1"}]},
            {"tool": "scoring_engine", "result": [{"id": "place-1"}]},
            {"tool": "scheduling_engine", "result": schedule},
        ],
    )

    assert "scheduling_engine" not in runnable_tool_names(session)
    assert "scheduling_engine" in runnable_tool_names(session, allow_replanning=True)


def test_planner_allows_retry_after_genuine_failure(monkeypatch):
    from app.services.langgraph.tool_inputs import runnable_tool_names

    schedule = {"status": "ok", "days": [{"items": []}]}
    current = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy"},
        tool_results=[
            {"tool": "candidate_retriever", "result": [{"id": "place-1"}]},
            {"tool": "scoring_engine", "result": [{"id": "place-1"}]},
            {"tool": "scheduling_engine", "result": schedule},
        ],
    )

    class FakeModel:
        def invoke(self, _prompt):
            return PlannerDecision(action="scheduling_engine")

    captured = []

    def model_factory(actions):
        captured.extend(actions)
        return FakeModel()

    monkeypatch.setattr(planner, "create_planner_model", model_factory)
    result = planner.planner_node(
        {
            "session": current,
            "last_failure": "Planning state validation failed.",
            "consecutive_failures": 1,
        }
    )

    assert "scheduling_engine" not in runnable_tool_names(current)
    assert "scheduling_engine" in captured
    assert result["planner_decision"].action == "scheduling_engine"


def test_malformed_manual_constraint_result_is_not_current(monkeypatch):
    from langchain_core.tools import tool

    from app.services.tools import registry

    malformed_result = {"status": "pass", "passed": True}

    @tool
    def constraint_validator(
        itinerary: dict, trip_requirements: dict, cost_estimate: dict
    ) -> dict:
        """Return a malformed result missing the constraint fields."""
        return malformed_result

    monkeypatch.setitem(registry.TOOLS, "constraint_validator", constraint_validator)
    state = create_state()
    state["session"].tool_results.extend(
        [
            {"tool": "scheduling_engine", "result": {}},
            {"tool": "cost_estimator", "result": {}},
        ]
    )
    state["planner_decision"] = PlannerDecision(action="constraint_validator")

    result = tool_execution_node(state)

    assert result["session"].constraint_result == malformed_result
    assert result["constraint_validation_current"] is False


def test_repeated_missing_constraint_provenance_uses_failure_guard(monkeypatch):
    from langchain_core.tools import tool

    from app.services.tools import registry

    @tool
    def weather_validator(schedule: dict) -> dict:
        """Return a successful weather check."""
        return {"status": "ok", "days": [], "warnings": []}

    monkeypatch.setitem(registry.TOOLS, "weather_validator", weather_validator)

    class FakePlannerModel:
        def invoke(self, _prompt):
            return PlannerDecision(
                action="weather_validator", arguments={"schedule": {}}
            )

    class FakeCriticModel:
        def __init__(self):
            self.calls = 0

        def invoke(self, _prompt):
            self.calls += 1
            return make_critic_decision(continue_planning=False, status="completed")

    critic_model = FakeCriticModel()
    monkeypatch.setattr(
        planner, "create_planner_model", lambda _runnable_actions: FakePlannerModel()
    )
    monkeypatch.setattr(critic, "create_critic_model", lambda: critic_model)
    session = AgentSession(
        goal="Plan a trip to Kandy",
        constraint_result={"status": "pass"},
        tool_results=[
            {"tool": "scheduling_engine", "result": {"status": "ok", "days": []}},
            {"tool": "weather_validator", "result": {"status": "ok"}},
        ],
    )

    result = planning_graph.invoke(
        {
            "session": session,
            "max_iterations": 2,
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }
    )

    assert result["constraint_validation_current"] is False
    assert critic_model.calls == 0
    assert result["session"].status == AgentSessionStatus.FAILED
    assert result["session"].iteration_count == 0


def test_schedule_and_cost_tools_invalidate_constraint_provenance(monkeypatch):
    from app.services.tools import registry

    class StubTool:
        def invoke(self, _arguments):
            return {"status": "ok"}

    for action in ("scheduling_engine", "route_optimizer", "cost_estimator"):
        monkeypatch.setitem(registry.TOOLS, action, StubTool())
        state = create_state()
        state["session"].tool_results.extend(
            [
                {"tool": "scoring_engine", "result": []},
                {"tool": "scheduling_engine", "result": {}},
                {"tool": "route_optimizer", "result": {}},
                {"tool": "cost_estimator", "result": {}},
            ]
        )
        state["planner_decision"] = PlannerDecision(action=action)

        result = tool_execution_node(state)

        assert result["constraint_validation_current"] is False
        assert result["session"].constraint_result is None


def test_critic_continuation_returns_feedback_to_planner(monkeypatch):
    from copy import deepcopy
    from importlib import import_module

    from langchain_core.tools import tool

    from app.services.tools import registry

    requirements = {
        "destination": "Kandy",
        "start_date": "2026-10-05",
        "end_date": "2026-10-05",
        "budget": 500,
        "travelers": 2,
    }
    schedule = {
        "status": "ok",
        "days": [
            {
                "date": "2026-10-05",
                "items": [
                    {
                        "candidate_id": "place-1",
                        "category": "attraction",
                        "name": "Lake walk",
                        "latitude": 7.29,
                        "longitude": 80.63,
                        "start_time": "09:00",
                        "end_time": "10:00",
                    }
                ],
            }
        ],
        "hotel_by_destination": {},
        "unscheduled": [],
        "warnings": [],
    }
    cost_estimate = {
        **{
            category: {"min": 10, "max": 20}
            for category in (
                "transport_intercity",
                "transport_local",
                "accommodation",
                "activities",
                "dining",
                "miscellaneous",
                "total",
            )
        },
        "travellers": 2,
        "warnings": [],
    }
    automatic_result = {
        "status": "pass",
        "passed": True,
        "constraints": {},
        "failed_constraints": [],
        "reasons": {},
    }
    suggestion = "Add a second outdoor activity on day two."
    constraint_calls = []

    @tool
    def cost_estimator(
        itinerary: dict, candidates: list[dict], trip_requirements: dict
    ) -> dict:
        """Return a usable estimate for the existing schedule."""
        return cost_estimate

    @tool
    def scheduling_engine(candidates: list[dict], trip_requirements: dict) -> dict:
        """Return a valid schedule if planning continues to another tool."""
        return schedule

    @tool
    def constraint_validator(
        itinerary: dict, trip_requirements: dict, cost_estimate: dict
    ) -> dict:
        """Return a passing automatic constraint result."""
        constraint_calls.append((itinerary, trip_requirements, cost_estimate))
        return automatic_result

    monkeypatch.setitem(registry.TOOLS, "cost_estimator", cost_estimator)
    monkeypatch.setitem(registry.TOOLS, "scheduling_engine", scheduling_engine)
    monkeypatch.setitem(registry.TOOLS, "constraint_validator", constraint_validator)

    class FakePlannerModel:
        def __init__(self):
            self.prompts = []
            self.provenance_at_second_prompt = None

        def invoke(self, prompt):
            self.prompts.append(prompt)
            if len(self.prompts) == 1:
                return PlannerDecision(
                    action="cost_estimator",
                    arguments={
                        "itinerary": schedule,
                        "candidates": [],
                        "trip_requirements": requirements,
                    },
                )
            if len(self.prompts) == 2:
                self.provenance_at_second_prompt = {
                    "constraint_result": deepcopy(session.constraint_result),
                    "latest_automatic_result": deepcopy(constraint_calls[-1]),
                }
            return PlannerDecision(
                action="scheduling_engine",
                arguments={"candidates": [], "trip_requirements": requirements},
            )

    class FakeCriticModel:
        def __init__(self):
            self.calls = 0
            self.decision = make_critic_decision(
                continue_planning=True,
                status=None,
                suggestions=[suggestion],
            )

        def invoke(self, _prompt):
            self.calls += 1
            return self.decision

    planner_model = FakePlannerModel()
    critic_model = FakeCriticModel()
    monkeypatch.setattr(
        planner, "create_planner_model", lambda _runnable_actions: planner_model
    )
    monkeypatch.setattr(critic, "create_critic_model", lambda: critic_model)
    graph_module = import_module("app.services.langgraph.planning_graph")
    original_route_after_critic = graph_module.route_after_critic
    critic_route_provenance = []

    def capture_critic_route(state):
        critic_route_provenance.append(
            (
                state.get("constraint_validation_current"),
                deepcopy(state["session"].constraint_result),
            )
        )
        return original_route_after_critic(state)

    monkeypatch.setattr(graph_module, "route_after_critic", capture_critic_route)
    session = AgentSession(
        goal="Plan a one-day trip to Kandy",
        trip_requirements=requirements,
        tool_results=[
            {"tool": "scoring_engine", "result": []},
            {"tool": "scheduling_engine", "result": schedule},
            {
                "tool": "weather_validator",
                "result": {"status": "ok", "days": [], "warnings": []},
            },
        ],
    )
    state = {
        "session": session,
        "max_iterations": 2,
        "planner_decision": None,
        "critic_decision": None,
        "last_failure": None,
        "consecutive_failures": 0,
    }

    result = graph_module.create_planning_graph().invoke(state)

    assert constraint_calls == [(schedule, requirements, cost_estimate)]
    assert critic_route_provenance == [(True, automatic_result)]
    assert critic_model.calls == 1
    assert critic_model.decision.continue_planning is True
    assert result["session"].status == AgentSessionStatus.COMPLETED
    assert result["session"].iteration_count == 0


def test_planning_graph_validates_constraints_before_critic(monkeypatch):
    from langchain_core.tools import tool

    from app.services.tools import registry

    calls = []
    scheduled_result = {
        "status": "ok",
        "days": [
            {
                "day_number": 1,
                "date": "2026-10-05",
                "items": [
                    {
                        "candidate_id": "place-1",
                        "category": "attraction",
                        "name": "Lake walk",
                        "latitude": 7.2906,
                        "longitude": 80.6337,
                        "start_time": "09:00",
                        "end_time": "10:00",
                        "duration_minutes": 60,
                        "opening_hours": None,
                    }
                ],
                "day_type": "arrival",
                "hotel_id": "hotel-1",
                "hotel_location": None,
                "warnings": [],
            },
            {
                "day_number": 2,
                "date": "2026-10-06",
                "day_type": "full",
                "items": [
                    {
                        "candidate_id": "place-1",
                        "category": "attraction",
                        "name": "Lake walk",
                        "latitude": 7.2906,
                        "longitude": 80.6337,
                        "start_time": "09:00",
                        "end_time": "10:00",
                        "duration_minutes": 60,
                        "opening_hours": None,
                    }
                ],
                "hotel_id": None,
                "hotel_location": None,
                "warnings": [],
            },
            {
                "day_number": 3,
                "date": "2026-10-07",
                "day_type": "departure",
                "items": [
                    {
                        "candidate_id": "place-1",
                        "category": "attraction",
                        "name": "Lake walk",
                        "latitude": 7.2906,
                        "longitude": 80.6337,
                        "start_time": "09:00",
                        "end_time": "10:00",
                        "duration_minutes": 60,
                        "opening_hours": None,
                    }
                ],
                "hotel_id": None,
                "hotel_location": None,
                "warnings": [],
            },
        ],
        "hotel_by_destination": {},
        "unscheduled": [],
        "warnings": [],
    }

    @tool
    def candidate_retriever(destination: str) -> list[dict]:
        """Return destination candidates."""
        calls.append(("candidate_retriever", destination))
        return [{"id": "place-1", "category": "attraction", "name": "Lake walk"}]

    @tool
    def scoring_engine(candidates: list[dict], preferences: dict) -> list[dict]:
        """Rank candidates."""
        calls.append(("scoring_engine", candidates, preferences))
        return [
            {**candidate, "final_score": 0.9, "score_breakdown": {}}
            for candidate in candidates
        ]

    @tool
    def scheduling_engine(candidates: list[dict], trip_requirements: dict) -> dict:
        """Build a day schedule."""
        calls.append(("scheduling_engine", candidates, trip_requirements))
        return scheduled_result

    @tool
    def route_optimizer(schedule: dict) -> dict:
        """Optimize attraction routes."""
        calls.append(("route_optimizer", schedule))
        result = {**schedule, "route_optimized": True}
        for day in result["days"]:
            day["route_optimization"] = {
                "reordered": False,
                "warning": None,
                "local_distance_km": 0.0,
            }
        return result

    @tool
    def weather_validator(schedule: dict) -> dict:
        """Stub a successful weather validation."""
        calls.append(("weather_validator", schedule))
        return {"status": "ok", "days": [], "warnings": []}

    @tool
    def cost_estimator(
        itinerary: dict, candidates: list[dict], trip_requirements: dict
    ) -> dict:
        """Stub a cost estimate for the schedule."""
        calls.append(("cost_estimator", itinerary, candidates, trip_requirements))
        categories = (
            "transport_intercity",
            "transport_local",
            "accommodation",
            "activities",
            "dining",
            "miscellaneous",
            "total",
        )
        return {
            **{category: {"min": 0, "max": 0} for category in categories},
            "travellers": 2,
            "warnings": [],
        }

    registered_stubs = {
        "candidate_retriever": candidate_retriever,
        "scoring_engine": scoring_engine,
        "scheduling_engine": scheduling_engine,
        "route_optimizer": route_optimizer,
        "weather_validator": weather_validator,
        "cost_estimator": cost_estimator,
    }
    for name, stub in registered_stubs.items():
        monkeypatch.setitem(registry.TOOLS, name, stub)

    requirements = {
        "destination": "Kandy",
        "start_date": "2026-10-05",
        "end_date": "2026-10-07",
        "budget": 500,
        "travelers": 2,
    }
    decisions = [
        PlannerDecision(
            action="candidate_retriever",
            arguments={"destination": requirements["destination"]},
        ),
        PlannerDecision(
            action="scoring_engine",
            arguments={
                "candidates": [
                    {"id": "place-1", "category": "attraction", "name": "Lake walk"}
                ],
                "preferences": requirements,
            },
        ),
        PlannerDecision(
            action="scheduling_engine",
            arguments={
                "candidates": [
                    {"id": "place-1", "category": "attraction", "name": "Lake walk"}
                ],
                "trip_requirements": requirements,
            },
        ),
        PlannerDecision(
            action="route_optimizer",
            arguments={"schedule": scheduled_result},
        ),
        PlannerDecision(
            action="weather_validator",
            arguments={"schedule": scheduled_result},
        ),
        PlannerDecision(
            action="cost_estimator",
            arguments={
                "itinerary": scheduled_result,
                "candidates": [
                    {"id": "place-1", "category": "attraction", "name": "Lake walk"}
                ],
                "trip_requirements": requirements,
            },
        ),
    ]

    class FakePlannerModel:
        def __init__(self):
            self.prompts = []

        def invoke(self, prompt):
            self.prompts.append(prompt)
            return decisions[len(self.prompts) - 1]

    class FakeCriticModel:
        def __init__(self):
            self.calls = 0
            self.prompts = []

        def invoke(self, prompt):
            self.prompts.append(prompt)
            self.calls += 1
            done = self.calls == 1
            return make_critic_decision(
                continue_planning=not done,
                status="completed" if done else None,
            )

    planner_model = FakePlannerModel()
    critic_model = FakeCriticModel()
    monkeypatch.setattr(
        planner, "create_planner_model", lambda _runnable_actions: planner_model
    )
    monkeypatch.setattr(critic, "create_critic_model", lambda: critic_model)

    session = AgentSession(
        goal="Plan a three-day trip to Kandy",
        trip_requirements=requirements,
    )
    result = planning_graph.invoke(
        {
            "session": session,
            "max_iterations": 8,
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }
    )

    updated = result["session"]
    expected_order = [*registered_stubs, "constraint_validator"]
    assert updated.tool_execution_order == expected_order
    assert [entry["tool"] for entry in updated.tool_results] == [
        name
        for tool_name in registered_stubs
        for name in (tool_name, "planning_state_validator")
    ] + ["constraint_validator"]
    assert updated.tool_results[6]["result"]["route_optimized"] is True
    assert updated.tool_results[8]["result"]["status"] == "ok"
    assert updated.tool_results[10]["result"]["total"]["max"] == 0
    assert updated.tool_results[12]["result"] == updated.constraint_result
    assert updated.tool_results[12]["tool"] == "constraint_validator"
    validation_statuses = [
        entry["result"]["status"]
        for entry in updated.tool_results
        if entry["tool"] == "planning_state_validator"
    ]
    assert validation_statuses == ["fail", "fail", "pass", "pass", "pass", "pass"]
    assert "ConstraintValidator result:" in critic_model.prompts[-1]
    for result_name in (
        "candidate_retriever",
        "scoring_engine",
        "scheduling_engine",
        "route_optimizer",
        "weather_validator",
        "cost_estimator",
        "constraint_validator",
    ):
        assert result_name in critic_model.prompts[-1]
    assert "Lake walk" in critic_model.prompts[-1]
    assert updated.status == AgentSessionStatus.COMPLETED
    assert result["constraint_validation_current"] is True
    assert len(planner_model.prompts) == 6
    assert critic_model.calls == 1

    # Each Planner turn receives only currently runnable tool names.
    assert "Plan a three-day trip to Kandy" in planner_model.prompts[0]
    assert "- candidate_retriever:" in planner_model.prompts[0]
    assert "- scoring_engine:" not in planner_model.prompts[0]
    assert "'destination': 'Kandy'" in planner_model.prompts[1]
    assert "- scoring_engine:" in planner_model.prompts[1]
    assert "- scheduling_engine:" not in planner_model.prompts[1]
    assert "Lake walk" not in planner_model.prompts[1]
    assert "supplies tool arguments" in planner_model.prompts[0].lower()
    assert "arguments=" not in planner_model.prompts[0]
    assert calls[0] == ("candidate_retriever", "Kandy")
    assert calls[1][0] == "scoring_engine"
    assert calls[1][2] == requirements
    assert calls[2][0] == "scheduling_engine"
    assert calls[2][2] == requirements
    assert calls[3] == ("route_optimizer", scheduled_result)
    assert calls[4] == ("weather_validator", scheduled_result)
    assert calls[5] == (
        "cost_estimator",
        updated.tool_results[6]["result"],
        [
            {
                "id": "place-1",
                "category": "attraction",
                "name": "Lake walk",
                "final_score": 0.9,
                "score_breakdown": {},
            }
        ],
        requirements,
    )


def test_registered_planning_tools_expose_registry_interface():
    from app.services.tools.registry import TOOLS

    required_arguments = {
        "candidate_retriever": {"destination"},
        "scoring_engine": {"candidates", "preferences"},
        "scheduling_engine": {"candidates", "trip_requirements"},
        "route_optimizer": {"schedule"},
        "weather_validator": {"schedule"},
        "cost_estimator": {"itinerary", "candidates", "trip_requirements"},
        "constraint_validator": {"itinerary", "trip_requirements", "cost_estimate"},
    }

    for name, arguments in required_arguments.items():
        registered = TOOLS[name]
        assert registered.name == name
        assert registered.description
        assert set(registered.args) == arguments
        assert callable(registered.invoke)


def _trace_test_context():
    import uuid

    from langgraph.runtime import Runtime

    class TraceSession:
        def __init__(self):
            self.added = []

        def add(self, record):
            self.added.append(record)

    db = TraceSession()
    planning_session_id = uuid.uuid4()
    runtime = Runtime(context={"db": db, "planning_session_id": planning_session_id})
    return db, planning_session_id, runtime


def test_tool_execution_persists_successful_trace(monkeypatch):
    from langchain_core.tools import tool

    from app.models.agent_execution_trace import AgentExecutionTrace
    from app.services.tools import registry

    @tool
    def candidate_retriever(destination: str) -> dict:
        """Return a candidate result."""
        return {"destination": destination, "count": 1}

    monkeypatch.setitem(registry.TOOLS, "candidate_retriever", candidate_retriever)
    db, planning_session_id, runtime = _trace_test_context()
    session = AgentSession(
        goal="Plan a trip",
        trip_requirements={"destination": "Kandy"},
        iteration_count=3,
    )
    state = {
        "session": session,
        "planner_decision": PlannerDecision(
            action="candidate_retriever", arguments={"destination": "Planner value"}
        ),
        "last_failure": None,
        "consecutive_failures": 0,
    }

    tool_execution_node(state, runtime)

    (trace,) = db.added
    assert isinstance(trace, AgentExecutionTrace)
    assert trace.planning_session_id == planning_session_id
    assert trace.tool_name == "candidate_retriever"
    assert trace.tool_input == {"destination": "Kandy"}
    assert trace.tool_output == {"destination": "Kandy", "count": 1}
    assert trace.success is True
    assert trace.iteration_number == 3


def test_tool_execution_persists_failed_trace_and_reraises(monkeypatch):
    import pytest
    from langchain_core.tools import tool

    from app.models.agent_execution_trace import AgentExecutionTrace
    from app.services.tools import registry

    @tool
    def candidate_retriever(destination: str) -> dict:
        """Raise while retrieving candidates."""
        raise RuntimeError("candidate service unavailable")

    monkeypatch.setitem(registry.TOOLS, "candidate_retriever", candidate_retriever)
    db, planning_session_id, runtime = _trace_test_context()
    state = {
        "session": AgentSession(
            goal="Plan a trip",
            trip_requirements={"destination": "Kandy"},
            iteration_count=2,
        ),
        "planner_decision": PlannerDecision(
            action="candidate_retriever", arguments={"destination": "Kandy"}
        ),
        "last_failure": None,
        "consecutive_failures": 0,
    }

    with pytest.raises(RuntimeError, match="candidate service unavailable"):
        tool_execution_node(state, runtime)

    (trace,) = db.added
    assert isinstance(trace, AgentExecutionTrace)
    assert trace.planning_session_id == planning_session_id
    assert trace.tool_name == "candidate_retriever"
    assert trace.tool_input == {"destination": "Kandy"}
    assert trace.tool_output == {
        "error_type": "RuntimeError",
        "error": "candidate service unavailable",
    }
    assert trace.success is False
    assert trace.iteration_number == 2


def test_scoring_engine_gets_latest_candidates_and_canonical_preferences(monkeypatch):
    from langchain_core.tools import tool

    from app.services.tools import registry

    canonical_candidates = [{"id": "stored", "category": "attraction"}]
    received = []

    @tool
    def scoring_engine(candidates: list[dict], preferences: dict) -> list[dict]:
        """Capture scoring inputs."""
        received.append((candidates, preferences))
        return candidates

    monkeypatch.setitem(registry.TOOLS, "scoring_engine", scoring_engine)
    requirements = {"destination": "Kandy", "interests": ["history"]}
    state = {
        "session": AgentSession(
            goal="Plan a trip",
            trip_requirements=requirements,
            tool_results=[
                {"tool": "candidate_retriever", "result": canonical_candidates}
            ],
        ),
        "planner_decision": PlannerDecision(action="scoring_engine"),
        "last_failure": None,
        "consecutive_failures": 0,
    }

    tool_execution_node(state)

    assert received == [(canonical_candidates, requirements)]


def test_weather_validator_keeps_scheduling_engine_source(monkeypatch):
    from langchain_core.tools import tool

    from app.services.tools import registry

    scheduled = {"status": "scheduled"}
    optimized = {"status": "optimized"}
    received = []

    @tool
    def weather_validator(schedule: dict) -> dict:
        """Capture the weather validation schedule."""
        received.append(schedule)
        return {"status": "ok"}

    monkeypatch.setitem(registry.TOOLS, "weather_validator", weather_validator)
    state = {
        "session": AgentSession(
            goal="Plan a trip",
            tool_results=[
                {"tool": "scheduling_engine", "result": scheduled},
                {"tool": "route_optimizer", "result": optimized},
            ],
        ),
        "planner_decision": PlannerDecision(action="weather_validator"),
        "last_failure": None,
        "consecutive_failures": 0,
    }

    tool_execution_node(state)

    assert received == [scheduled]


def test_missing_tool_prerequisite_does_not_invoke_with_fabricated_arguments():
    state = {
        "session": AgentSession(
            goal="Plan a trip",
            trip_requirements={"destination": "Kandy"},
        ),
        "planner_decision": PlannerDecision(action="scoring_engine"),
        "last_failure": None,
        "consecutive_failures": 0,
    }

    result = tool_execution_node(state)

    assert (
        result["last_failure"]
        == "Missing canonical input for selected tool: scoring_engine"
    )
    assert result["consecutive_failures"] == 1
    assert state["session"].tool_results == []
    assert state["session"].tool_execution_order == []


def test_planner_structured_actions_are_runnable_and_advance_prerequisites(
    monkeypatch,
):
    from app.services.langgraph.tool_inputs import runnable_tool_names

    candidates = [{"id": "a1", "category": "attraction", "name": "Lake"}]
    retrieved = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy"},
        tool_results=[{"tool": "candidate_retriever", "result": candidates}],
    )
    assert runnable_tool_names(retrieved) == ["scoring_engine"]

    scored = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy"},
        tool_results=[
            {"tool": "candidate_retriever", "result": candidates},
            {"tool": "scoring_engine", "result": candidates},
        ],
    )
    eligible = runnable_tool_names(scored)
    assert eligible == ["scheduling_engine"]
    assert "route_optimizer" not in eligible

    class FakeModel:
        def invoke(self, prompt):
            self.prompt = prompt
            # Simulate a nonconforming stub/provider. The boundary guard must
            # still prevent an unavailable action reaching tool execution.
            return PlannerDecision(action="scheduling_engine")

    model = FakeModel()
    captured_actions = []

    def model_factory(runnable_actions):
        captured_actions.extend(runnable_actions)
        return model

    monkeypatch.setattr(planner, "create_planner_model", model_factory)
    result = planner.planner_node(
        {
            "session": retrieved,
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }
    )

    assert captured_actions == ["scoring_engine"]
    assert "scoring_engine" in model.prompt
    assert "scheduling_engine:" not in model.prompt
    assert result["planner_decision"].action == "scoring_engine"

    from langchain_core.tools import tool

    from app.services.tools import registry

    received = []

    @tool
    def scoring_engine(candidates: list[dict], preferences: dict) -> list[dict]:
        """Capture the fallback's canonical scoring inputs."""
        received.append((candidates, preferences))
        return candidates

    monkeypatch.setitem(registry.TOOLS, "scoring_engine", scoring_engine)
    execution_state = {
        "session": retrieved,
        "planner_decision": result["planner_decision"],
        "last_failure": None,
        "consecutive_failures": 0,
    }
    execution = tool_execution_node(execution_state)

    assert received == [(candidates, retrieved.trip_requirements)]
    assert execution["last_failure"] is None
    assert retrieved.tool_execution_order == ["scoring_engine"]


def test_planner_structured_schema_restricts_action_enum(monkeypatch):
    captured = {}

    class FakeChatModel:
        def with_structured_output(self, schema):
            captured["schema"] = schema
            return schema

    monkeypatch.setattr(planner, "ChatOpenAI", lambda **_kwargs: FakeChatModel())
    schema = planner.create_planner_model(["scoring_engine"])

    json_schema = schema.model_json_schema()
    action_ref = json_schema["properties"]["action"]["$ref"].rsplit("/", 1)[-1]
    assert json_schema["$defs"][action_ref]["enum"] == ["scoring_engine"]
    edit_plan_ref = json_schema["properties"]["edit_plan"]["anyOf"][0]["$ref"].rsplit(
        "/", 1
    )[-1]
    assert json_schema["$defs"][edit_plan_ref]["properties"]["operation"]["enum"] == [
        "remove",
        "add",
        "replace",
        "move",
        "change",
    ]


def test_itinerary_edit_plan_covers_supported_operations():
    examples = [
        {"operation": "remove", "target_item": "Jaffna Fort", "source_day": 2},
        {"operation": "add", "target_item": "Nallur Temple", "destination_day": 1},
        {
            "operation": "replace",
            "target_item": "Jaffna Fort",
            "replacement_item": "another attraction",
        },
        {
            "operation": "move",
            "target_item": "Nallur Temple",
            "source_day": 1,
            "destination_day": 2,
        },
        {
            "operation": "change",
            "target_item": "morning activity",
            "source_day": 1,
            "requested_change": "something cheaper",
        },
    ]

    plans = [ItineraryEditPlan.model_validate(example) for example in examples]

    assert [plan.operation for plan in plans] == [
        "remove",
        "add",
        "replace",
        "move",
        "change",
    ]


def test_planner_returns_edit_plan_and_supplies_context(monkeypatch):
    itinerary = {
        "days": [{"day_number": 2, "items": [{"id": "item-2", "title": "Jaffna Fort"}]}]
    }
    edit_plan = ItineraryEditPlan(
        operation="remove", target_item="Jaffna Fort", source_day=2
    )
    session = AgentSession(
        goal="Plan a trip to Jaffna",
        trip_requirements={"destination": "Jaffna", "budget": 500},
    )

    class FakeModel:
        def invoke(self, prompt):
            self.prompt = prompt
            return PlannerDecision(action="candidate_retriever", edit_plan=edit_plan)

    model = FakeModel()
    monkeypatch.setattr(planner, "create_planner_model", lambda _actions: model)

    result = planner.planner_node(
        {
            "session": session,
            "current_itinerary": itinerary,
            "latest_user_message": "Remove Jaffna Fort from day 2.",
            "last_failure": None,
        }
    )

    assert result["planner_decision"].action == "candidate_retriever"
    assert result["planner_decision"].edit_plan == edit_plan
    assert "Remove Jaffna Fort from day 2." in model.prompt
    assert "Jaffna Fort" in model.prompt
    assert "'budget': 500" in model.prompt
    assert "do not apply or persist" in model.prompt


@pytest.mark.parametrize("operation", ["add", "remove", "replace", "move", "change"])
def test_planning_graph_ends_after_any_edit_plan(monkeypatch, operation):
    edit_plan = ItineraryEditPlan(
        operation=operation,
        target_item="Kandy View Point",
        destination_day=2,
        replacement_item="New attraction" if operation == "replace" else None,
        requested_change="cheaper" if operation == "change" else None,
    )

    class FakeModel:
        def invoke(self, _prompt):
            return PlannerDecision(action="candidate_retriever", edit_plan=edit_plan)

    monkeypatch.setattr(planner, "create_planner_model", lambda _actions: FakeModel())
    session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy"},
    )

    result = planning_graph.invoke(
        {
            "session": session,
            "current_itinerary": {"days": [{"day_number": 2, "items": []}]},
            "latest_user_message": "Add Kandy View Point to day 2.",
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }
    )

    assert result["planner_decision"].edit_plan == edit_plan
    assert session.tool_results == []


def test_planner_prompt_recognizes_add_requests(monkeypatch):
    cases = [
        ("Add Kandy View Point", '"Add Kandy View Point"'),
        ("Add Kandy View Point to day 2", '"Add Kandy View Point to day 2"'),
        ("I want to visit Kandy View Point", '"I want to visit Kandy View Point"'),
    ]

    for message, example in cases:

        class FakeModel:
            def invoke(self, prompt):
                self.prompt = prompt
                return PlannerDecision(action="candidate_retriever")

        model = FakeModel()
        monkeypatch.setattr(
            planner, "create_planner_model", lambda _actions, model=model: model
        )
        session = AgentSession(
            goal="Plan a trip to Kandy",
            trip_requirements={"destination": "Kandy"},
        )
        planner.planner_node(
            {
                "session": session,
                "current_itinerary": {"days": [{"day_number": 1, "items": []}]},
                "latest_user_message": message,
                "last_failure": None,
            }
        )

        assert message in model.prompt
        assert example in model.prompt
        assert 'operation="add"' in model.prompt
        assert "target_item" in model.prompt
        assert "destination_day only when the user specifies a day" in model.prompt
        assert "destination_time only when the user specifies a time" in model.prompt
        assert "Do not invent unknown" in model.prompt
        assert "do not apply or persist" in model.prompt


def test_scheduling_engine_gets_canonical_date_objects(monkeypatch):
    from datetime import date

    from langchain_core.tools import tool

    from app.services.tools import registry

    received = {}
    received_candidates = []

    @tool
    def scheduling_engine(candidates: list[dict], trip_requirements: dict) -> dict:
        """Capture canonical scheduling inputs."""
        received_candidates.extend(candidates)
        received.update(trip_requirements)
        return {"status": "ok", "days": []}

    monkeypatch.setitem(registry.TOOLS, "scheduling_engine", scheduling_engine)
    canonical_start = date(2026, 10, 5)
    canonical_end = date(2026, 10, 7)
    session = AgentSession(
        goal="Plan a trip",
        iteration_count=4,
        trip_requirements={
            "destination": "Kandy",
            "start_date": canonical_start,
            "end_date": canonical_end,
        },
        tool_results=[{"tool": "scoring_engine", "result": [{"id": "stored"}]}],
    )
    state = {
        "session": session,
        "planner_decision": PlannerDecision(
            action="scheduling_engine",
            arguments={
                "candidates": [{"id": "Planner value"}],
                "trip_requirements": {
                    "destination": "Kandy",
                    "start_date": "2026-10-05",
                    "end_date": "2026-10-07",
                },
            },
        ),
        "last_failure": None,
        "consecutive_failures": 0,
    }

    tool_execution_node(state)

    assert received_candidates == [{"id": "stored"}]
    assert received["start_date"] is canonical_start
    assert received["end_date"] is canonical_end
    assert isinstance(received["start_date"], date)
    assert isinstance(received["end_date"], date)


def test_route_optimizer_uses_stored_schedule_instead_of_planner_schedule(monkeypatch):
    from langchain_core.tools import tool

    from app.services.tools import registry

    valid_schedule = {
        "status": "ok",
        "days": [
            {
                "day_number": 1,
                "date": "2026-10-05",
                "day_type": "full",
                "items": [],
            }
        ],
    }
    received_schedules = []

    @tool
    def route_optimizer(schedule: dict) -> dict:
        """Capture the schedule passed to route optimization."""
        received_schedules.append(schedule)
        return schedule

    monkeypatch.setitem(registry.TOOLS, "route_optimizer", route_optimizer)
    session = AgentSession(
        goal="Plan a trip",
        iteration_count=2,
        tool_results=[
            {"tool": "scheduling_engine", "result": valid_schedule},
        ],
    )
    state = {
        "session": session,
        "planner_decision": PlannerDecision(
            action="route_optimizer",
            arguments={"schedule": {"status": "ok", "days": [None]}},
        ),
        "last_failure": None,
        "consecutive_failures": 0,
    }

    tool_execution_node(state)

    assert received_schedules == [valid_schedule]
    assert received_schedules[0]["days"][0]["day_number"] == 1


def test_route_optimizer_prefers_latest_optimizer_result(monkeypatch):
    from langchain_core.tools import tool

    from app.services.tools import registry

    scheduling_result = {"status": "ok", "days": [{"day_number": 1}]}
    optimized_result = {
        "status": "ok",
        "days": [{"day_number": 1, "route_optimization": {"reordered": True}}],
    }
    received_schedules = []

    @tool
    def route_optimizer(schedule: dict) -> dict:
        """Capture the schedule passed to route optimization."""
        received_schedules.append(schedule)
        return schedule

    monkeypatch.setitem(registry.TOOLS, "route_optimizer", route_optimizer)
    session = AgentSession(
        goal="Plan a trip",
        iteration_count=3,
        tool_results=[
            {"tool": "scheduling_engine", "result": scheduling_result},
            {"tool": "route_optimizer", "result": optimized_result},
        ],
    )
    state = {
        "session": session,
        "planner_decision": PlannerDecision(
            action="route_optimizer",
            arguments={"schedule": {"status": "ok", "days": [None]}},
        ),
        "last_failure": None,
        "consecutive_failures": 0,
    }

    tool_execution_node(state)

    assert received_schedules == [optimized_result]


def test_cost_estimator_uses_stored_route_optimizer_result(monkeypatch):
    from langchain_core.tools import tool

    from app.models.agent_execution_trace import AgentExecutionTrace
    from app.services.tools import registry

    optimized_itinerary = {
        "status": "ok",
        "days": [{"day_number": 1, "route_optimization": {"local_distance_km": 4}}],
    }
    scored_candidates = [{"id": "a1", "category": "attraction"}]
    requirements = {"destination": "Kandy", "travelers": 2}
    received = []

    @tool
    def cost_estimator(
        itinerary: dict, candidates: list[dict], trip_requirements: dict
    ) -> dict:
        """Capture cost estimation inputs."""
        received.append((itinerary, candidates, trip_requirements))
        return {"total": {"min": 1, "max": 2}}

    monkeypatch.setitem(registry.TOOLS, "cost_estimator", cost_estimator)
    db, planning_session_id, runtime = _trace_test_context()
    state = {
        "session": AgentSession(
            goal="Plan a trip",
            iteration_count=5,
            trip_requirements=requirements,
            tool_results=[
                {"tool": "scoring_engine", "result": scored_candidates},
                {"tool": "route_optimizer", "result": optimized_itinerary},
            ],
        ),
        "planner_decision": PlannerDecision(
            action="cost_estimator",
            arguments={
                "itinerary": {"status": "ok", "days": ["malformed day"]},
                "candidates": [],
                "trip_requirements": {},
            },
        ),
        "last_failure": None,
        "consecutive_failures": 0,
    }

    tool_execution_node(state, runtime)

    assert received == [(optimized_itinerary, scored_candidates, requirements)]
    (trace,) = db.added
    assert isinstance(trace, AgentExecutionTrace)
    assert trace.planning_session_id == planning_session_id
    assert trace.tool_name == "cost_estimator"
    assert trace.tool_input == {
        "itinerary": optimized_itinerary,
        "candidates": scored_candidates,
        "trip_requirements": requirements,
    }


def test_cost_estimator_falls_back_to_stored_scheduling_result(monkeypatch):
    from langchain_core.tools import tool

    from app.services.tools import registry

    scheduled_itinerary = {
        "status": "ok",
        "days": [{"day_number": 1, "items": []}],
    }
    received = []

    @tool
    def cost_estimator(
        itinerary: dict, candidates: list[dict], trip_requirements: dict
    ) -> dict:
        """Capture cost estimation itinerary."""
        received.append(itinerary)
        return {"total": {"min": 1, "max": 2}}

    monkeypatch.setitem(registry.TOOLS, "cost_estimator", cost_estimator)
    state = {
        "session": AgentSession(
            goal="Plan a trip",
            trip_requirements={"destination": "Kandy"},
            iteration_count=4,
            tool_results=[
                {"tool": "scoring_engine", "result": []},
                {"tool": "scheduling_engine", "result": scheduled_itinerary},
            ],
        ),
        "planner_decision": PlannerDecision(
            action="cost_estimator",
            arguments={
                "itinerary": {"status": "ok", "days": ["malformed day"]},
                "candidates": [],
                "trip_requirements": {},
            },
        ),
        "last_failure": None,
        "consecutive_failures": 0,
    }

    tool_execution_node(state)

    assert received == [scheduled_itinerary]


def test_critic_continuation_planner_increments_iteration_count(monkeypatch):
    from app.services.langgraph.planning_graph import (
        critic_continuation_planner_node,
    )

    prompts = []

    class FakeModel:
        def invoke(self, prompt):
            prompts.append(prompt)
            return PlannerDecision(
                action="candidate_retriever", arguments={"destination": "Kandy"}
            )

    monkeypatch.setattr(
        planner, "create_planner_model", lambda _runnable_actions: FakeModel()
    )
    session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy"},
    )
    state = {
        "session": session,
        "planner_decision": None,
        "critic_decision": None,
        "last_failure": None,
        "consecutive_failures": 0,
    }

    result = critic_continuation_planner_node(state)

    assert result["planner_decision"].action == "candidate_retriever"
    assert session.iteration_count == 1
    assert "Current iteration:\n1" in prompts[0]


def test_planner_prompt_supports_implicit_remove_requests(monkeypatch):
    session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy"},
    )

    class FakeModel:
        def invoke(self, prompt):
            self.prompt = prompt
            return PlannerDecision(action="candidate_retriever")

    model = FakeModel()
    monkeypatch.setattr(planner, "create_planner_model", lambda _actions: model)

    planner.planner_node(
        {
            "session": session,
            "current_itinerary": {
                "days": [
                    {
                        "day_number": 2,
                        "items": [{"id": "item-1", "title": "Bahirawakanda Temple"}],
                    }
                ]
            },
            "latest_user_message": "I don't want to visit Bahirawakanda Temple.",
            "last_failure": None,
        }
    )

    assert "I don't want to visit X" in model.prompt
    assert "REMOVE operation" in model.prompt
    assert "first check whether the latest user message" in model.prompt
    assert "before considering normal planning" in model.prompt
    assert (
        "only when the latest message does not request an itinerary edit"
        in model.prompt
    )
