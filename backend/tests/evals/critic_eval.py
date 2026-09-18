import json
import os

from app.schemas.agent_session import AgentSession
from app.services.langgraph.critic import critic_node


DATASET_PATH = os.path.join(
    os.path.dirname(__file__),
    "planner_dataset.json",
)


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def run_critic_eval():
    if not os.getenv("GOOGLE_API_KEY"):
        print("GOOGLE_API_KEY is not configured.")
        print("Critic evaluation skipped.")
        return

    dataset = load_dataset()

    critic_cases = [case for case in dataset if case["type"] == "critic"]

    passed = 0
    failed = 0

    print("=== Critic Evaluation ===")

    for case in critic_cases:
        session = AgentSession(
            user_request=case["request"],
            trip_preferences=case["preferences"],
            tool_results=case["tool_results"],
            tool_execution_order=case["tool_execution_order"],
        )

        state = {
            "session": session,
            "planner_decision": None,
            "critic_decision": None,
            "last_failure": None,
            "consecutive_failures": 0,
        }

        try:
            result = critic_node(state)

            decision = result["critic_decision"]

            actual_continue = decision.continue_planning
            expected_continue = case["expected_continue_planning"]

            actual_status = decision.status
            expected_status = case["expected_status"]

            continue_matches = actual_continue == expected_continue

            # Only compare status when the dataset specifies
            # an expected terminal status.
            status_matches = expected_status is None or actual_status == expected_status

            if continue_matches and status_matches:
                passed += 1
                result_status = "PASS"
            else:
                failed += 1
                result_status = "FAIL"

            print(
                f"{result_status} | "
                f"{case['id']} | "
                f"Expected continue: {expected_continue} | "
                f"Actual continue: {actual_continue} | "
                f"Expected status: {expected_status} | "
                f"Actual status: {actual_status}"
            )

        except Exception as exc:
            failed += 1

            print(f"FAIL | " f"{case['id']} | " f"Error: {exc}")

    total = passed + failed
    match_rate = (passed / total * 100) if total else 0

    print()
    print("=== Evaluation Summary ===")
    print(f"Total cases: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Decision match rate: {match_rate:.2f}%")


if __name__ == "__main__":
    run_critic_eval()
