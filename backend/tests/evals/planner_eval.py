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
    if not os.getenv("GOOGLE_API_KEY"):
        print("GOOGLE_API_KEY is not configured.")
        print("Planner evaluation skipped.")
        return

    dataset = load_dataset()

    planner_cases = [case for case in dataset if case["type"] == "planner"]

    passed = 0
    failed = 0

    print("=== Planner Evaluation ===")

    for case in planner_cases:
        session = AgentSession(
            user_request=case["request"],
            trip_preferences=case["preferences"],
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
            expected_action = case["expected_action"]

            if actual_action == expected_action:
                passed += 1
                status = "PASS"
            else:
                failed += 1
                status = "FAIL"

            print(
                f"{status} | "
                f"{case['id']} | "
                f"Expected: {expected_action} | "
                f"Actual: {actual_action}"
            )

        except Exception as exc:
            failed += 1

            print(f"FAIL | " f"{case['id']} | " f"Error: {exc}")

    total = passed + failed

    accuracy = (passed / total * 100) if total else 0

    print()
    print("=== Evaluation Summary ===")
    print(f"Total cases: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Action match rate: {accuracy:.2f}%")


if __name__ == "__main__":
    run_planner_eval()
