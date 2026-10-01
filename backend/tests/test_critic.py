import pytest
from pydantic import ValidationError

from app.schemas.agent_session import AgentSession, AgentSessionStatus
from app.schemas.planning import CriticDecision
from app.services.langgraph import critic, planner
from app.services.langgraph.critic import route_after_critic


def assessment(score, reasoning):
    return {"score": score, "reasoning": reasoning}


def decision(**overrides):
    result = {
        "continue_planning": False,
        "status": "completed",
        "reason": "The itinerary meets the stated planning needs.",
        "variety": assessment(4, "The itinerary includes different kinds of places."),
        "daily_balance": assessment(
            4, "Activities are distributed across the trip days."
        ),
        "interest_match": assessment(
            5, "The selected places reflect the user's stated interests."
        ),
        "pacing": assessment(4, "Each day has a manageable number of activities."),
        "suggestions": [],
    }
    result.update(overrides)
    return CriticDecision(**result)


def session(**updates):
    values = {
        "goal": "Plan a three-day culture and nature trip to Kandy.",
        "trip_requirements": {
            "destination": "Kandy",
            "interests": ["culture", "nature"],
        },
        "constraint_result": {
            "status": "pass",
            "failed_constraints": [],
            "reasons": {},
        },
        "tool_results": [
            {"tool": "weather_validator", "result": {"status": "ok"}},
            {"tool": "constraint_validator", "result": {"status": "pass"}},
        ],
    }
    values.update(updates)
    return AgentSession(**values)


def test_bad_plan_returns_scores_and_actionable_feedback(monkeypatch):
    response = decision(
        continue_planning=True,
        status=None,
        variety=assessment(
            1, "The schedule repeats the same kind of attraction each day."
        ),
        daily_balance=assessment(
            2, "The first day has many more activities than the last day."
        ),
        suggestions=["Replace one repeated attraction with a nature activity."],
    )

    class FakeModel:
        def invoke(self, _prompt):
            return response

    monkeypatch.setattr(critic, "create_critic_model", lambda: FakeModel())
    current = session()
    result = critic.critic_node({"session": current})

    assert result["critic_decision"].variety.score == 1
    assert result["critic_decision"].daily_balance.score == 2
    assert result["critic_decision"].suggestions == [
        "Replace one repeated attraction with a nature activity."
    ]
    assert current.critic_result == response.model_dump(mode="json")


def test_critic_decision_is_persisted_to_execution_trace(monkeypatch):
    import uuid

    from langgraph.runtime import Runtime

    response = decision(
        continue_planning=True,
        status=None,
        reason="The itinerary omits a requested hiking experience.",
        suggestions=["Add a suitable hiking stop on day two."],
    )

    class FakeModel:
        def invoke(self, _prompt):
            return response

    class FakeDB:
        def __init__(self):
            self.records = []

        def add(self, record):
            self.records.append(record)

    monkeypatch.setattr(critic, "create_critic_model", lambda: FakeModel())
    current = session(iteration_count=4)
    planning_session_id = uuid.uuid4()
    db = FakeDB()
    runtime = Runtime(context={"db": db, "planning_session_id": planning_session_id})

    result = critic.critic_node({"session": current}, runtime=runtime)

    assert result["critic_decision"] == response
    assert len(db.records) == 1
    trace = db.records[0]
    assert trace.tool_name == "critic"
    assert trace.planning_session_id == planning_session_id
    assert trace.iteration_number == 4
    assert trace.success is True
    assert trace.tool_input["goal"] == current.goal
    assert trace.tool_input["trip_requirements"] == current.trip_requirements
    assert trace.tool_input["constraint_result"] == current.constraint_result
    assert trace.tool_input["iteration_count"] == 4
    assert trace.tool_output["continue_planning"] is True
    assert trace.tool_output["status"] is None
    assert trace.tool_output["reason"] == response.reason
    assert trace.tool_output["suggestions"] == response.suggestions
    assert trace.tool_output["variety"] == response.variety.model_dump()


def test_good_plan_completes_without_unnecessary_suggestions(monkeypatch):
    response = decision()

    class FakeModel:
        def invoke(self, _prompt):
            return response

    monkeypatch.setattr(critic, "create_critic_model", lambda: FakeModel())
    result = critic.critic_node({"session": session()})

    assert result["critic_decision"].status == "completed"
    assert result["critic_decision"].suggestions == []


@pytest.mark.parametrize("status", ["completed", "best_effort", "infeasible", "failed"])
def test_all_terminal_statuses_are_accepted(status):
    assert decision(status=status).status == status


def test_criterion_reasoning_accepts_e_g_abbreviation():
    result = decision(variety=assessment(3, "The plan includes options, e.g. museums."))
    assert result.variety.reasoning == "The plan includes options, e.g. museums."


def test_criterion_reasoning_accepts_decimal_number():
    result = decision(variety=assessment(3, "The estimated walk is 3.5 kilometers."))
    assert result.variety.reasoning == "The estimated walk is 3.5 kilometers."


def test_criterion_reasoning_rejects_multiple_sentences():
    with pytest.raises(ValidationError):
        decision(variety=assessment(3, "First sentence. Second sentence."))


def test_critic_failure_uses_planning_termination_path(monkeypatch):
    class FailingModel:
        def invoke(self, _prompt):
            raise ValueError("invalid structured Critic output")

    monkeypatch.setattr(critic, "create_critic_model", lambda: FailingModel())
    current = session()
    state = {
        "session": current,
        "critic_decision": None,
        "last_failure": None,
        "consecutive_failures": 0,
        "max_iterations": 8,
    }

    result = critic.critic_node(state)
    state.update(result)

    assert result["critic_decision"] is None
    assert route_after_critic(state) == "end"
    assert current.status == AgentSessionStatus.FAILED


def test_planner_prompt_contains_latest_critic_feedback(monkeypatch):
    captured = []

    class FakeModel:
        def invoke(self, prompt):
            captured.append(prompt)
            from app.schemas.planning import PlannerDecision

            return PlannerDecision(
                action="candidate_retriever", arguments={"destination": "Kandy"}
            )

    monkeypatch.setattr(
        planner, "create_planner_model", lambda _runnable_actions: FakeModel()
    )
    feedback = {
        "variety": {"score": 1, "reasoning": "The itinerary repeats similar places."},
        "suggestions": ["Add a nature stop on day two."],
    }
    current = session(critic_result=feedback)
    planner.planner_node({"session": current})

    assert "Add a nature stop on day two." in captured[0]
    assert "The itinerary repeats similar places." in captured[0]


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("completed", AgentSessionStatus.COMPLETED),
        ("best_effort", AgentSessionStatus.BEST_EFFORT),
        ("infeasible", AgentSessionStatus.INFEASIBLE),
        ("failed", AgentSessionStatus.FAILED),
    ],
)
def test_terminal_critic_statuses_route_to_end(status, expected):
    selected = decision(status=status)
    current = session()
    state = {
        "session": current,
        "critic_decision": selected,
        "max_iterations": 8,
        "consecutive_failures": 0,
        "constraint_validation_current": True,
    }

    assert route_after_critic(state) == "end"
    assert current.status == expected


def test_critic_prompt_includes_planning_state_validation_result(monkeypatch):
    captured = []

    class FakeModel:
        def invoke(self, prompt):
            captured.append(prompt)
            return decision()

    monkeypatch.setattr(critic, "create_critic_model", lambda: FakeModel())
    validator_result = {
        "status": "pass",
        "passed": True,
        "checks": {
            "itinerary": {
                "status": "pass",
                "reasons": ["critic-context-validation-marker"],
            }
        },
    }
    current = session(
        tool_results=[{"tool": "planning_state_validator", "result": validator_result}]
    )

    critic.critic_node({"session": current})

    assert "planning_state_validator" in captured[0]
    assert "critic-context-validation-marker" in captured[0]
