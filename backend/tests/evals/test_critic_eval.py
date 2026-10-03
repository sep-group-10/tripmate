from app.schemas.planning import CriticDecision
from tests.evals import critic_eval


def _decision(*, continue_planning, status):
    assessment = {"score": 3, "reasoning": "The itinerary has a clear structure."}
    return CriticDecision(
        continue_planning=continue_planning,
        status=status,
        variety=assessment,
        daily_balance=assessment,
        interest_match=assessment,
        pacing=assessment,
        suggestions=["Spread activities across the requested days."]
        if continue_planning
        else [],
    )


def _case(*, continue_planning, status):
    return {
        "id": "critic_test",
        "request": "Plan a trip to Kandy.",
        "preferences": {"destination": "Kandy", "interests": ["culture"]},
        "tool_results": [{"tool": "scheduling_engine", "result": {"status": "ok"}}],
        "tool_execution_order": ["scheduling_engine"],
        "constraint_result": {"status": "pass", "failed_constraints": []},
        "expected_continue_planning": continue_planning,
        "expected_status": status,
    }


def test_build_critic_state_preserves_dataset_inputs():
    case = _case(continue_planning=True, status=None)

    state = critic_eval.build_critic_state(case)

    assert state["session"].goal == case["request"]
    assert state["session"].trip_requirements == case["preferences"]
    assert state["session"].tool_results == case["tool_results"]
    assert state["session"].tool_execution_order == case["tool_execution_order"]
    assert state["session"].constraint_result == case["constraint_result"]
    assert state["critic_decision"] is None


def test_evaluate_case_matches_continuation_and_requires_null_status(monkeypatch):
    case = _case(continue_planning=True, status=None)
    captured = {}

    def fake_critic_node(state):
        captured["state"] = state
        return {"critic_decision": _decision(continue_planning=True, status=None)}

    monkeypatch.setattr(critic_eval, "critic_node", fake_critic_node)

    result = critic_eval.evaluate_case(case)

    assert captured["state"]["session"].goal == case["request"]
    assert result == {
        "decision": True,
        "status": None,
        "structurally_valid": True,
        "decision_match": True,
        "status_match": True,
        "combined_match": True,
        "error": None,
    }


def test_evaluate_case_compares_terminal_status(monkeypatch):
    case = _case(continue_planning=False, status="completed")
    monkeypatch.setattr(
        critic_eval,
        "critic_node",
        lambda _state: {
            "critic_decision": _decision(continue_planning=False, status="best_effort")
        },
    )

    result = critic_eval.evaluate_case(case)

    assert result["structurally_valid"] is True
    assert result["decision_match"] is True
    assert result["status_match"] is False
    assert result["combined_match"] is False


def test_evaluate_case_marks_missing_decision_structurally_invalid(monkeypatch):
    monkeypatch.setattr(
        critic_eval, "critic_node", lambda _state: {"critic_decision": None}
    )

    result = critic_eval.evaluate_case(_case(continue_planning=True, status=None))

    assert result["structurally_valid"] is False
    assert result["decision_match"] is False
    assert result["status_match"] is False
    assert result["combined_match"] is False
