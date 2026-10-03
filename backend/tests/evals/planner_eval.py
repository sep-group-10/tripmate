import json
import os

from app.schemas.agent_session import AgentSession
from app.services.langgraph.planner import planner_node

DATASET_PATH = os.path.join(
    os.path.dirname(__file__),
    "planner_dataset.json",
)


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def run_planner_eval():
    if not os.getenv("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY is not configured.")
        print("Planner evaluation skipped.")
        return

    dataset = load_dataset()

    planner_cases = [case for case in dataset if case["type"] == "planner"]

    passed = 0
    failed = 0
    exact_action_cases = 0
    valid_action_set_cases = 0

    print("=== Planner Evaluation ===")

    for case in planner_cases:
        session = AgentSession(
            goal=case["request"],
            trip_requirements=case["preferences"],
            tool_results=case.get("tool_results", []),
        )

        state = {
            "session": session,
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }

        try:
            result = planner_node(state)

            decision = result["planner_decision"]

            actual_action = decision.action
            expected_action = case.get("expected_action")
            valid_actions = case.get("valid_actions")

            if expected_action is not None:
                exact_action_cases += 1
                is_valid = actual_action == expected_action
                expectation = f"Expected: {expected_action}"
            elif valid_actions is not None:
                valid_action_set_cases += 1
                is_valid = actual_action in valid_actions
                expectation = f"Valid actions: {valid_actions}"
            else:
                raise ValueError(
                    "Planner case requires expected_action or valid_actions"
                )

            if is_valid:
                passed += 1
                status = "PASS"
            else:
                failed += 1
                status = "FAIL"

            print(
                f"{status} | "
                f"{case['id']} | "
                f"{expectation} | Actual: {actual_action}"
            )

        except (ValueError, TypeError, RuntimeError) as exc:
            failed += 1

            print(
                f"FAIL | {case['id']} | "
                f"Expected: {case.get('expected_action')} | "
                f"Valid actions: {case.get('valid_actions')} | Error: {exc}"
            )

    total = passed + failed

    valid_decision_rate = (passed / total * 100) if total else 0

    print()
    print("=== Evaluation Summary ===")
    print(f"Total cases: {total}")
    print(f"Exact-action cases: {exact_action_cases}")
    print(f"Valid-action-set cases: {valid_action_set_cases}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Overall valid decision rate: {valid_decision_rate:.2f}%")


if __name__ == "__main__":
    run_planner_eval()
