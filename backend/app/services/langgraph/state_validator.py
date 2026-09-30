"""Structural validation for the planning graph's current AgentSession."""

from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from math import isfinite
from typing import Any

from app.schemas.agent_session import AgentSession
from app.services.tools.registry import TOOLS
from app.services.tools.scheduling_config import ScheduleStatus

_STATE_VALIDATOR_NAME = "planning_state_validator"
_SCHEDULE_STATUSES = {status.value for status in ScheduleStatus}
_WEATHER_STATUSES = {"ok", "warning", "problem", "could_not_check"}
_COST_CATEGORIES = (
    "transport_intercity",
    "transport_local",
    "accommodation",
    "activities",
    "dining",
    "miscellaneous",
    "total",
)


def _usable_date(value: Any) -> bool:
    if isinstance(value, (date, datetime)):
        return True
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _usable_number(value: Any) -> bool:
    if isinstance(value, bool) or value is None:
        return False
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return False
    return number.is_finite()


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _record_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(record, dict) for record in value)


def _range_dict(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and _usable_number(value.get("min"))
        and _usable_number(value.get("max"))
    )


def _schedule_dict(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("status") in _SCHEDULE_STATUSES
        and isinstance(value.get("days"), list)
        and isinstance(value.get("hotel_by_destination"), dict)
        and isinstance(value.get("unscheduled"), list)
        and isinstance(value.get("warnings"), list)
    )


def _expected_result(tool_name: str, result: Any) -> bool:
    if tool_name in {"candidate_retriever", "scoring_engine"}:
        if not _record_list(result):
            return False
        if not all(
            _nonempty_string(record.get("id"))
            and _nonempty_string(record.get("category"))
            and _nonempty_string(record.get("name"))
            for record in result
        ):
            return False
        if tool_name == "scoring_engine":
            return all(
                _usable_number(record.get("final_score"))
                and isinstance(record.get("score_breakdown"), dict)
                for record in result
            )
        return True

    if tool_name == "scheduling_engine":
        return _schedule_dict(result)
    if tool_name == "route_optimizer":
        return _schedule_dict(result) and all(
            isinstance(day, dict) and isinstance(day.get("route_optimization"), dict)
            for day in result["days"]
        )
    if tool_name == "weather_validator":
        return (
            isinstance(result, dict)
            and result.get("status") in _WEATHER_STATUSES
            and isinstance(result.get("days"), list)
            and isinstance(result.get("warnings"), list)
        )
    if tool_name == "cost_estimator":
        return (
            isinstance(result, dict)
            and all(_range_dict(result.get(category)) for category in _COST_CATEGORIES)
            and isinstance(result.get("travellers"), int)
            and isinstance(result.get("warnings"), list)
        )
    if tool_name == "constraint_validator":
        return (
            isinstance(result, dict)
            and result.get("status") in {"pass", "fail"}
            and isinstance(result.get("passed"), bool)
            and isinstance(result.get("constraints"), dict)
            and isinstance(result.get("failed_constraints"), list)
            and isinstance(result.get("reasons"), dict)
        )
    if tool_name == _STATE_VALIDATOR_NAME:
        return (
            isinstance(result, dict)
            and result.get("status") in {"pass", "fail"}
            and isinstance(result.get("passed"), bool)
            and isinstance(result.get("failed_checks"), list)
            and isinstance(result.get("checks"), dict)
        )
    return False


def is_valid_tool_result(tool_name: str, result: Any) -> bool:
    """Return whether a tool result has the usable graph shape."""

    return _expected_result(tool_name, result)


def is_valid_constraint_result(result: Any) -> bool:
    """Return whether a ConstraintValidator result has the usable graph shape."""

    return is_valid_tool_result("constraint_validator", result)


def _usable_time(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        time.fromisoformat(value)
    except ValueError:
        return False
    return True


def _coordinate(value: Any, lower: float, upper: float) -> bool:
    if isinstance(value, bool) or value is None:
        return False
    try:
        coordinate = float(value)
    except (TypeError, ValueError):
        return False
    return isfinite(coordinate) and lower <= coordinate <= upper


def _has_coordinates(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and _coordinate(value.get("latitude"), -90, 90)
        and _coordinate(value.get("longitude"), -180, 180)
    )


def _check_trip_requirements(session: AgentSession) -> list[str]:
    requirements = session.trip_requirements
    if not isinstance(requirements, dict):
        return ["trip_requirements must be an object."]

    reasons: list[str] = []
    if not _nonempty_string(requirements.get("destination")):
        reasons.append("destination is missing or unusable.")
    for field in ("start_date", "end_date"):
        if not _usable_date(requirements.get(field)):
            reasons.append(f"{field} is missing or unusable.")
    if not _usable_number(requirements.get("budget")):
        reasons.append("budget is missing or unusable.")
    travelers = requirements.get("travelers")
    if isinstance(travelers, bool) or not isinstance(travelers, int):
        reasons.append("travelers is missing or unusable.")
    return reasons


def _check_tool_results(session: AgentSession) -> list[str]:
    entries = session.tool_results
    if not isinstance(entries, list) or not entries:
        return ["tool_results must contain at least one tool result."]

    known_tools = set(TOOLS) | {_STATE_VALIDATOR_NAME}
    reasons: list[str] = []
    for index, entry in enumerate(entries):
        label = f"tool_results[{index}]"
        if not isinstance(entry, dict):
            reasons.append(f"{label} must be an object.")
            continue
        tool_name = entry.get("tool")
        if not _nonempty_string(tool_name) or tool_name not in known_tools:
            reasons.append(f"{label} has an unknown or missing tool name.")
            continue
        result = entry.get("result")
        if result is None:
            reasons.append(f"{label} ({tool_name}) has a null result.")
        elif not _expected_result(tool_name, result):
            reasons.append(f"{label} ({tool_name}) has a malformed result.")
    return reasons


def _latest_schedule(session: AgentSession) -> Any:
    if not isinstance(session.tool_results, list):
        return None
    for entry in reversed(session.tool_results):
        if isinstance(entry, dict) and entry.get("tool") == "scheduling_engine":
            return entry.get("result")
    return None


def _check_itinerary(session: AgentSession) -> tuple[list[str], list[str]]:
    schedule = _latest_schedule(session)
    if not isinstance(schedule, dict):
        return ["A scheduling_engine result is missing or is not an object."], [
            "No scheduled place items are available."
        ]

    itinerary_reasons: list[str] = []
    days = schedule.get("days")
    if not isinstance(days, list):
        return ["SchedulingEngine days must be a list."], [
            "No scheduled place items are available."
        ]
    if not days:
        return ["SchedulingEngine returned no days."], [
            "No scheduled place items are available."
        ]

    items: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for day_index, day in enumerate(days):
        if not isinstance(day, dict):
            itinerary_reasons.append(f"days[{day_index}] must be an object.")
            continue
        day_items = day.get("items")
        if not isinstance(day_items, list):
            itinerary_reasons.append(f"days[{day_index}].items must be a list.")
            continue
        items.extend((day, item) for item in day_items if isinstance(item, dict))
        if any(not isinstance(item, dict) for item in day_items):
            itinerary_reasons.append(
                f"days[{day_index}].items contains a non-object item."
            )

    item_reasons: list[str] = []
    if not items:
        item_reasons.append("At least one scheduled item is required.")

    for index, (day, item) in enumerate(items):
        label = f"scheduled item {index}"
        for field in ("candidate_id", "category", "name"):
            if not _nonempty_string(item.get(field)):
                item_reasons.append(f"{label} has a missing or unusable {field}.")
        for field in ("start_time", "end_time"):
            if not _usable_time(item.get(field)):
                item_reasons.append(f"{label} has a missing or unusable {field}.")
        item_location = {
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
        }
        if not _has_coordinates(item_location) and not _has_coordinates(
            day.get("hotel_location")
        ):
            item_reasons.append(f"{label} has no usable coordinates or day location.")

    return itinerary_reasons, item_reasons


def validate_planning_state(session: AgentSession) -> dict[str, Any]:
    """Validate required session structure and a usable scheduled itinerary."""

    itinerary_reasons, item_reasons = _check_itinerary(session)
    checks = {
        "trip_requirements": {
            "reasons": _check_trip_requirements(session),
        },
        "tool_results": {
            "reasons": _check_tool_results(session),
        },
        "itinerary": {"reasons": itinerary_reasons},
        "itinerary_items": {"reasons": item_reasons},
    }
    for check in checks.values():
        check["status"] = "fail" if check["reasons"] else "pass"

    failed_checks = [
        name for name, check in checks.items() if check["status"] == "fail"
    ]
    return {
        "status": "fail" if failed_checks else "pass",
        "passed": not failed_checks,
        "failed_checks": failed_checks,
        "checks": checks,
    }
