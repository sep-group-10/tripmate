"""Live, model-dependent evaluation of critic_node decisions only."""

import json
import os

from app.schemas.agent_session import AgentSession
from app.schemas.planning import CriticDecision
from app.services.langgraph.critic import critic_node

DATASET_PATH = os.path.join(
    os.path.dirname(__file__),
    "planner_dataset.json",
)


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def build_critic_state(case):
    """Build the same Critic node input used by the live evaluation."""
    session = AgentSession(
        goal=case["request"],
        trip_requirements=case["preferences"],
        tool_results=case["tool_results"],
        tool_execution_order=case["tool_execution_order"],
        constraint_result=case.get("constraint_result"),
    )

    return {
        "session": session,
        "planner_decision": None,
        "critic_decision": None,
        "last_failure": None,
        "consecutive_failures": 0,
    }


def evaluate_case(case):
    """Run one Critic case and compare only defined decision/status fields."""
    state = build_critic_state(case)
    result = critic_node(state)
    decision = result.get("critic_decision") if isinstance(result, dict) else None
    structurally_valid = isinstance(decision, CriticDecision)

    if not structurally_valid:
        return {
            "decision": None,
            "status": None,
            "structurally_valid": False,
            "decision_match": False,
            "status_match": False,
            "combined_match": False,
            "error": result.get("last_failure") if isinstance(result, dict) else None,
        }

    actual_continue = decision.continue_planning
    actual_status = decision.status
    expected_continue = case["expected_continue_planning"]
    expected_status = case["expected_status"]

    # A null expected status means this is a continuing case and the Critic
    # must leave status unset, as specified by the Critic prompt.
    return {
        "decision": actual_continue,
        "status": actual_status,
        "structurally_valid": True,
        "decision_match": actual_continue == expected_continue,
        "status_match": actual_status == expected_status,
        "combined_match": (
            actual_continue == expected_continue and actual_status == expected_status
        ),
        "error": None,
    }


def run_critic_eval():
    print("=== Live Critic Evaluation (model-dependent) ===")
    print("Measures critic_node() decisions only; does not evaluate graph routing.")

    if not os.getenv("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY is not configured.")
        print("Live Critic evaluation skipped.")
        return

    critic_cases = [case for case in load_dataset() if case["type"] == "critic"]
    decision_passes = 0
    decision_failures = 0
    status_passes = 0
    status_failures = 0
    combined_passes = 0
    combined_failures = 0
    structurally_valid_count = 0

    for case in critic_cases:
        try:
            result = evaluate_case(case)
        except Exception as exc:
            result = {
                "decision": None,
                "status": None,
                "structurally_valid": False,
                "decision_match": False,
                "status_match": False,
                "combined_match": False,
                "error": f"{type(exc).__name__}: {exc}",
            }

        structurally_valid_count += int(result["structurally_valid"])
        decision_passes += int(result["decision_match"])
        status_passes += int(result["status_match"])
        combined_passes += int(result["combined_match"])

        if not result["decision_match"]:
            decision_failures += 1
        if not result["status_match"]:
            status_failures += 1
        if not result["combined_match"]:
            combined_failures += 1

        case_result = "PASS" if result["combined_match"] else "FAIL"
        print(
            f"{case_result} | {case['id']} | "
            f"Structurally valid: {result['structurally_valid']} | "
            f"Expected continue: {case['expected_continue_planning']} | "
            f"Actual continue: {result['decision']} | "
            f"Expected status: {case['expected_status']} | "
            f"Actual status: {result['status']}"
            + (f" | Error: {result['error']}" if result["error"] else "")
        )

    total_cases = len(critic_cases)
    decision_cases = total_cases
    status_cases = total_cases
    decision_match_rate = (
        decision_passes / decision_cases * 100 if decision_cases else 0
    )
    status_match_rate = status_passes / status_cases * 100 if status_cases else 0
    overall_match_rate = combined_passes / total_cases * 100 if total_cases else 0

    print()
    print("=== Live Evaluation Summary ===")
    print(f"Total cases: {total_cases}")
    print(f"Structurally valid decisions: {structurally_valid_count}/{total_cases}")
    print(f"Decision cases: {decision_cases}")
    print(f"Decision passes/failures: {decision_passes}/{decision_failures}")
    print(f"Status cases: {status_cases}")
    print(f"Status passes/failures: {status_passes}/{status_failures}")
    print(f"Combined case passes/failures: {combined_passes}/{combined_failures}")
    print(f"Decision match rate: {decision_match_rate:.2f}%")
    print(f"Status match rate: {status_match_rate:.2f}%")
    print(f"Overall case match rate: {overall_match_rate:.2f}%")


if __name__ == "__main__":
    run_critic_eval()
