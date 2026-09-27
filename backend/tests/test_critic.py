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


def test_criterion_reasoning_must_be_exactly_one_sentence():
    with pytest.raises(ValidationError):
        decision(variety=assessment(3, "First sentence. Second sentence."))


def test_planner_prompt_contains_latest_critic_feedback(monkeypatch):
    captured = []

    class FakeModel:
        def invoke(self, prompt):
            captured.append(prompt)
            from app.schemas.planning import PlannerDecision

            return PlannerDecision(
                action="candidate_retriever", arguments={"destination": "Kandy"}
            )

    monkeypatch.setattr(planner, "create_planner_model", lambda: FakeModel())
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
