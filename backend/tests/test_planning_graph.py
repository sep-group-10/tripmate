import inspect

from app.schemas.agent_session import AgentSession, AgentSessionStatus
from app.schemas.planning import CriticDecision, PlannerDecision
from app.services.langgraph import critic, planner
from app.services.langgraph.planning_graph import (
    planning_graph,
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


def test_planning_state_validation_routes_invalid_session_to_planner():
    state = create_state()
    result = {"status": "fail", "failed_checks": ["itinerary"]}
    state["session"].tool_results.append(
        {"tool": "planning_state_validator", "result": result}
    )

    assert route_after_planning_state_validation(state) == "planner"
    assert state["session"].tool_results[-1]["result"] == result


def test_planning_state_validation_preserves_iteration_guard():
    state = create_state(iteration_count=8, max_iterations=8)
    state["session"].tool_results.append(
        {"tool": "planning_state_validator", "result": {"status": "fail"}}
    )

    assert route_after_planning_state_validation(state) == "end"
    assert state["session"].status == AgentSessionStatus.BEST_EFFORT


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


def test_failed_constraint_validation_respects_max_iteration_guard():
    state = create_state(iteration_count=8, max_iterations=8)
    state["session"].constraint_result = {"status": "fail"}

    assert route_after_constraint_validation(state) == "end"
    assert state["session"].status == AgentSessionStatus.BEST_EFFORT


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


def test_critic_can_route_back_to_planner():
    state = create_state(continue_planning=True)

    result = route_after_critic(state)

    assert result == "planner"


def test_critic_can_finish_with_completed_status():
    state = create_state(
        continue_planning=False,
        status="completed",
    )
    result = route_after_critic(state)

    assert result == "end"
    assert state["session"].status == AgentSessionStatus.COMPLETED


def test_critic_cannot_finish_before_weather_validation():
    state = create_state(
        continue_planning=False,
        status="completed",
    )
    state["session"].tool_results.clear()

    result = route_after_critic(state)

    assert result == "planner"


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
    monkeypatch.setattr(planner, "create_planner_model", lambda: planner_model)
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

    assert result["session"].status == AgentSessionStatus.COMPLETED
    assert result["session"].tool_execution_order == [
        "scheduling_engine",
        "weather_validator",
        "cost_estimator",
        "constraint_validator",
    ]
    assert [entry["tool"] for entry in result["session"].tool_results] == [
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


def test_invalid_state_routes_back_to_planner_and_preserves_validation_result(
    monkeypatch,
):
    from langchain_core.tools import tool

    from app.services.tools import registry

    @tool
    def candidate_retriever(destination: str) -> list[dict]:
        """Return structurally valid candidates without a schedule."""
        return [{"id": "place-1", "category": "attraction", "name": destination}]

    monkeypatch.setitem(registry.TOOLS, "candidate_retriever", candidate_retriever)

    class FakePlannerModel:
        def __init__(self):
            self.prompts = []

        def invoke(self, prompt):
            self.prompts.append(prompt)
            return PlannerDecision(
                action="candidate_retriever",
                arguments={"destination": "Kandy"},
            )

    class FakeCriticModel:
        def __init__(self):
            self.calls = 0

        def invoke(self, _prompt):
            self.calls += 1
            return make_critic_decision(continue_planning=False, status="completed")

    planner_model = FakePlannerModel()
    critic_model = FakeCriticModel()
    monkeypatch.setattr(planner, "create_planner_model", lambda: planner_model)
    monkeypatch.setattr(critic, "create_critic_model", lambda: critic_model)

    session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={
            "destination": "Kandy",
            "start_date": "2026-10-05",
            "end_date": "2026-10-05",
            "budget": 50000,
            "travelers": 2,
        },
    )
    result = planning_graph.invoke(
        {
            "session": session,
            "max_iterations": 3,
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }
    )

    assert len(planner_model.prompts) == 3
    assert "planning_state_validator" in planner_model.prompts[1]
    assert "scheduling_engine result is missing" in planner_model.prompts[1]
    assert critic_model.calls == 0
    assert result["session"].status == AgentSessionStatus.BEST_EFFORT
    state_results = [
        entry["result"]
        for entry in result["session"].tool_results
        if entry["tool"] == "planning_state_validator"
    ]
    assert len(state_results) == 3
    assert all(result["status"] == "fail" for result in state_results)


def test_real_planner_uses_current_agent_session_fields(monkeypatch):
    class FakeModel:
        def __init__(self):
            self.prompts = []

        def invoke(self, prompt):
            self.prompts.append(prompt)
            return PlannerDecision(
                action="candidate_retriever", arguments={"destination": "Kandy"}
            )

    model = FakeModel()
    monkeypatch.setattr(planner, "create_planner_model", lambda: model)
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
    assert session.iteration_count == 1
    assert "Plan a trip to Kandy" in model.prompts[0]
    assert "'destination': 'Kandy'" in model.prompts[0]


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


def test_different_failures_reset_consecutive_failure_count():
    """Different failures must not be treated as a deadlock."""

    state = create_state(
        consecutive_failures=1,
        continue_planning=True,
    )

    state["last_failure"] = "Unknown tool: first_tool"
    state["planner_decision"] = PlannerDecision(
        action="second_tool",
        arguments={},
    )

    result = tool_execution_node(state)

    assert result["last_failure"] == "Unknown tool: second_tool"
    assert result["consecutive_failures"] == 1


def test_same_failure_increments_consecutive_failure_count():
    """The same failure must increase the deadlock counter."""

    state = create_state(
        consecutive_failures=1,
        continue_planning=True,
    )

    failure = "Unknown tool: missing_tool"
    state["last_failure"] = failure
    state["planner_decision"] = PlannerDecision(
        action="missing_tool",
        arguments={},
    )

    result = tool_execution_node(state)

    assert result["last_failure"] == failure
    assert result["consecutive_failures"] == 2


def test_planner_selected_constraint_validator_cannot_bypass_automatic_gate(
    monkeypatch,
):
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
    validator_calls = []

    @tool
    def constraint_validator(
        itinerary: dict, trip_requirements: dict, cost_estimate: dict
    ) -> dict:
        """Return a passing result for the manual Planner-selected call."""
        validator_calls.append((itinerary, trip_requirements, cost_estimate))
        return {
            "status": "pass",
            "passed": True,
            "constraints": {},
            "failed_constraints": [],
            "reasons": {},
        }

    @tool
    def weather_validator(schedule: dict) -> dict:
        """Return a successful weather check."""
        return {"status": "ok", "days": [], "warnings": []}

    monkeypatch.setitem(registry.TOOLS, "constraint_validator", constraint_validator)
    monkeypatch.setitem(registry.TOOLS, "weather_validator", weather_validator)

    class FakePlannerModel:
        def __init__(self):
            self.calls = 0

        def invoke(self, _prompt):
            self.calls += 1
            if self.calls == 1:
                return PlannerDecision(
                    action="constraint_validator",
                    arguments={
                        "itinerary": schedule,
                        "trip_requirements": requirements,
                        "cost_estimate": cost_estimate,
                    },
                )
            return PlannerDecision(
                action="weather_validator",
                arguments={"schedule": schedule},
            )

    class FakeCriticModel:
        def __init__(self):
            self.calls = 0

        def invoke(self, _prompt):
            self.calls += 1
            return make_critic_decision(continue_planning=False, status="completed")

    planner_model = FakePlannerModel()
    critic_model = FakeCriticModel()
    monkeypatch.setattr(planner, "create_planner_model", lambda: planner_model)
    monkeypatch.setattr(critic, "create_critic_model", lambda: critic_model)
    session = AgentSession(
        goal="Plan a one-day trip to Kandy",
        trip_requirements=requirements,
        tool_results=[
            {"tool": "scheduling_engine", "result": schedule},
            {
                "tool": "weather_validator",
                "result": {"status": "ok", "days": [], "warnings": []},
            },
            {"tool": "cost_estimator", "result": cost_estimate},
        ],
    )

    result = planning_graph.invoke(
        {
            "session": session,
            "max_iterations": 3,
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }
    )

    assert validator_calls == [(schedule, requirements, cost_estimate)]
    assert result["session"].constraint_result["status"] == "pass"
    assert result["constraint_validation_current"] is False
    assert planner_model.calls == 3
    assert critic_model.calls == 0
    assert result["session"].status == AgentSessionStatus.BEST_EFFORT


def test_missing_constraint_provenance_cannot_invoke_critic(monkeypatch):
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
    monkeypatch.setattr(planner, "create_planner_model", lambda: FakePlannerModel())
    monkeypatch.setattr(critic, "create_critic_model", lambda: critic_model)
    session = AgentSession(
        goal="Plan a trip to Kandy",
        constraint_result={"status": "pass"},
        tool_results=[{"tool": "weather_validator", "result": {"status": "ok"}}],
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

    assert "constraint_validation_current" not in result
    assert critic_model.calls == 0
    assert result["session"].status == AgentSessionStatus.BEST_EFFORT


def test_schedule_and_cost_tools_invalidate_constraint_provenance(monkeypatch):
    from app.services.tools import registry

    class StubTool:
        def invoke(self, _arguments):
            return {"status": "ok"}

    for action in ("scheduling_engine", "route_optimizer", "cost_estimator"):
        monkeypatch.setitem(registry.TOOLS, action, StubTool())
        state = create_state()
        state["planner_decision"] = PlannerDecision(action=action, arguments={})

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
    monkeypatch.setattr(planner, "create_planner_model", lambda: planner_model)
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
    assert planner_model.provenance_at_second_prompt == {
        "constraint_result": automatic_result,
        "latest_automatic_result": (schedule, requirements, cost_estimate),
    }
    # Critic ran only after the graph routed through automatic PASS, and its
    # continuation sent the Planner the same current passing result above.
    assert result["constraint_validation_current"] is False
    assert critic_model.calls == 1
    assert critic_model.decision.continue_planning is True
    assert planner_model.prompts[1].count(suggestion) == 1
    assert result["session"].status == AgentSessionStatus.BEST_EFFORT


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
                "hotel_id": None,
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
    monkeypatch.setattr(planner, "create_planner_model", lambda: planner_model)
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
    assert updated.status == AgentSessionStatus.COMPLETED
    assert result["constraint_validation_current"] is True
    assert len(planner_model.prompts) == 6
    assert critic_model.calls == 1

    # Each new Planner turn sees current session output and tool argument schemas.
    assert "Plan a three-day trip to Kandy" in planner_model.prompts[0]
    assert "'destination': 'Kandy'" in planner_model.prompts[1]
    for name in expected_order:
        assert name in planner_model.prompts[0]
    assert '"trip_requirements"' in planner_model.prompts[0]
    assert calls[0] == ("candidate_retriever", "Kandy")
    assert calls[1][0] == "scoring_engine"
    assert calls[1][2] == requirements
    assert calls[2][0] == "scheduling_engine"
    assert calls[2][2] == requirements
    assert calls[3] == ("route_optimizer", scheduled_result)
    assert calls[4] == ("weather_validator", scheduled_result)
    assert calls[5] == (
        "cost_estimator",
        scheduled_result,
        [{"id": "place-1", "category": "attraction", "name": "Lake walk"}],
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
