"""Deterministic Planner evaluation using real runnable-action derivation."""

from types import SimpleNamespace

import pytest

from app.schemas.agent_session import AgentSession
from app.services.langgraph import planner
from app.services.langgraph.tool_inputs import runnable_tool_names

SCHEDULE = {"status": "ok", "days": [{"items": []}]}
CANDIDATES = [{"id": "place-1"}]


def _session(action):
    """Return a real AgentSession whose only runnable planner action is action."""
    results = []
    requirements = {"destination": "Kandy"}
    if action == "scoring_engine":
        results = [{"tool": "candidate_retriever", "result": CANDIDATES}]
    elif action == "scheduling_engine":
        results = [
            {"tool": "candidate_retriever", "result": CANDIDATES},
            {"tool": "scoring_engine", "result": CANDIDATES},
        ]
    elif action == "route_optimizer":
        results = [
            {"tool": "candidate_retriever", "result": CANDIDATES},
            {"tool": "scoring_engine", "result": CANDIDATES},
            {"tool": "scheduling_engine", "result": SCHEDULE},
            {"tool": "weather_validator", "result": {"status": "ok"}},
            {"tool": "cost_estimator", "result": {"total": {"min": 0, "max": 0}}},
        ]
    elif action == "weather_validator":
        results = [
            {"tool": "candidate_retriever", "result": CANDIDATES},
            {"tool": "scoring_engine", "result": CANDIDATES},
            {"tool": "scheduling_engine", "result": SCHEDULE},
            {"tool": "route_optimizer", "result": SCHEDULE},
            {"tool": "cost_estimator", "result": {"total": {"min": 0, "max": 0}}},
        ]
    elif action == "cost_estimator":
        results = [
            {"tool": "candidate_retriever", "result": CANDIDATES},
            {"tool": "scoring_engine", "result": CANDIDATES},
            {"tool": "scheduling_engine", "result": SCHEDULE},
            {"tool": "route_optimizer", "result": SCHEDULE},
            {"tool": "weather_validator", "result": {"status": "ok"}},
        ]
    return AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements=requirements,
        tool_results=results,
    )


@pytest.mark.parametrize(
    "action",
    [
        "candidate_retriever",
        "scoring_engine",
        "scheduling_engine",
        "route_optimizer",
        "weather_validator",
        "cost_estimator",
    ],
)
def test_deterministic_planner_action_evaluation(monkeypatch, action):
    session = _session(action)
    runnable = runnable_tool_names(session)
    assert runnable == [action]
    assert "constraint_validator" not in runnable

    class FakeModel:
        def invoke(self, _prompt):
            return SimpleNamespace(action=action, edit_plan=None)

    captured = {}

    def fake_factory(runnable_actions):
        captured["runnable_actions"] = runnable_actions
        return FakeModel()

    monkeypatch.setattr(planner, "create_planner_model", fake_factory)
    state = {
        "session": session,
        "planner_decision": None,
        "critic_decision": None,
        "last_failure": None,
        "consecutive_failures": 0,
    }

    result = planner.planner_node(state)

    assert captured["runnable_actions"] == [action]
    assert result["planner_decision"].action == action


def test_constraint_validator_is_never_offered_to_planner():
    session = AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements={"destination": "Kandy"},
        tool_results=[
            {"tool": "candidate_retriever", "result": CANDIDATES},
            {"tool": "scoring_engine", "result": CANDIDATES},
            {"tool": "scheduling_engine", "result": SCHEDULE},
            {"tool": "cost_estimator", "result": {"total": {"min": 0, "max": 0}}},
        ],
    )
    assert "constraint_validator" not in runnable_tool_names(session)
