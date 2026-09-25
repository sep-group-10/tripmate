import json
import os
from collections import Counter
from decimal import Decimal
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from app.services.preference_processor import PreferenceProcessor

DATASET_PATH = os.path.join(
    os.path.dirname(__file__),
    "preference_dataset.json",
)

EVALUATED_FIELDS = [
    "intent",
    "destination",
    "dates",
    "duration_days",
    "budget",
    "travelers",
    "interests",
    "missing_fields",
]


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def build_messages(messages: list[dict[str, str]]):
    """Convert dataset messages into LangChain chat messages."""
    converted_messages = []

    for message in messages:
        if message["role"] == "user":
            converted_messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            converted_messages.append(AIMessage(content=message["content"]))
        else:
            raise ValueError(f"Unsupported message role: {message['role']}")

    return converted_messages


def evaluate_result(result, expected: dict[str, Any]) -> dict[str, bool]:
    """Compare only preference fields explicitly expected by a dataset case."""
    field_matches = {}

    if "intent" in expected:
        field_matches["intent"] = result.intent == expected["intent"]

    if "destination" in expected:
        field_matches["destination"] = result.destination == expected["destination"]

    if "start_date" in expected or "end_date" in expected:
        field_matches["dates"] = (
            result.start_date.isoformat() if result.start_date else None
        ) == expected.get("start_date") and (
            result.end_date.isoformat() if result.end_date else None
        ) == expected.get("end_date")

    if "duration_days" in expected:
        field_matches["duration_days"] = (
            result.duration_days == expected["duration_days"]
        )

    if "budget" in expected:
        field_matches["budget"] = result.budget == Decimal(str(expected["budget"]))

    if "travelers" in expected:
        field_matches["travelers"] = result.travelers == expected["travelers"]

    if "interests" in expected:
        field_matches["interests"] = Counter(result.interests) == Counter(
            expected["interests"]
        )

    if "missing_fields" in expected:
        field_matches["missing_fields"] = Counter(result.missing_fields) == Counter(
            expected["missing_fields"]
        )

    return field_matches


def run_preference_eval():
    if not os.getenv("GOOGLE_API_KEY"):
        print("GOOGLE_API_KEY is not configured.")
        print("Preference evaluation skipped.")
        return

    dataset = load_dataset()
    processor = PreferenceProcessor()
    field_totals = {field: 0 for field in EVALUATED_FIELDS}
    field_passes = {field: 0 for field in EVALUATED_FIELDS}
    passed = 0
    failed = 0

    print("=== Preference Evaluation ===")

    for case in dataset:
        try:
            result = processor.process(build_messages(case["messages"]))
            field_matches = evaluate_result(result, case["expected"])

            for field, matches in field_matches.items():
                field_totals[field] += 1
                if matches:
                    field_passes[field] += 1

            failed_fields = [
                field for field, matches in field_matches.items() if not matches
            ]

            if failed_fields:
                failed += 1
                status = "FAIL"
                details = f"Failed fields: {', '.join(failed_fields)}"
            else:
                passed += 1
                status = "PASS"
                details = "All expected fields matched"

            print(f"{status} | {case['id']} | {details}")

            for field in failed_fields:
                if field == "dates":
                    expected_value = {
                        "start_date": case["expected"].get("start_date"),
                        "end_date": case["expected"].get("end_date"),
                    }
                    actual_value = {
                        "start_date": (
                            result.start_date.isoformat() if result.start_date else None
                        ),
                        "end_date": (
                            result.end_date.isoformat() if result.end_date else None
                        ),
                    }
                else:
                    expected_value = case["expected"][field]
                    actual_value = getattr(result, field)

                print(f"Expected: {field} = {expected_value}")
                print(f"Actual:   {field} = {actual_value}")

        except Exception as error:  # noqa: BLE001
            failed += 1
            print(f"FAIL | {case['id']} | Error: {type(error).__name__}")

    total = passed + failed

    print()
    print("=== Evaluation Summary ===")
    print(f"Total cases: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    for field in EVALUATED_FIELDS:
        evaluated = field_totals[field]
        accuracy = (field_passes[field] / evaluated * 100) if evaluated else 0
        print(f"{field} accuracy: {accuracy:.2f}% ({field_passes[field]}/{evaluated})")


if __name__ == "__main__":
    run_preference_eval()
