"""Deterministic hard-constraint checks for a scheduled trip."""

from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from langchain_core.tools import tool


def _as_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def _as_decimal(value: Any) -> Decimal | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    return result if result.is_finite() else None


def _check(status: str, reason: str) -> dict[str, str]:
    return {"status": status, "reason": reason}


def validate_constraints(
    itinerary: dict[str, Any],
    trip_requirements: dict[str, Any],
    cost_estimate: dict[str, Any],
) -> dict[str, Any]:
    """Validate budget, scheduled dates, scheduler feasibility and explicit capacities."""

    checks: dict[str, dict[str, str]] = {}

    budget = _as_decimal(trip_requirements.get("budget"))
    total = cost_estimate.get("total") or {}
    estimated_max = _as_decimal(total.get("max")) if isinstance(total, dict) else None
    if budget is None or estimated_max is None:
        checks["budget"] = _check(
            "fail", "Budget or maximum estimated total is missing or invalid."
        )
    elif estimated_max <= budget:
        checks["budget"] = _check(
            "pass",
            f"Maximum estimated total ({estimated_max}) is within budget ({budget}).",
        )
    else:
        checks["budget"] = _check(
            "fail",
            f"Maximum estimated total ({estimated_max}) exceeds the trip budget ({budget}).",
        )

    start_date = _as_date(trip_requirements.get("start_date"))
    end_date = _as_date(trip_requirements.get("end_date"))
    days = itinerary.get("days")
    day_dates = (
        [_as_date(day.get("date")) for day in days if isinstance(day, dict)]
        if isinstance(days, list)
        else []
    )
    duration_reasons: list[str] = []
    if start_date is None or end_date is None or end_date < start_date:
        duration_reasons.append("Trip start_date/end_date are missing or invalid.")
    elif not isinstance(days, list):
        duration_reasons.append("Itinerary days are missing or invalid.")
    else:
        invalid_day_count = len(day_dates) != len(days) or any(
            day_date is None for day_date in day_dates
        )
        if invalid_day_count:
            duration_reasons.append(
                "One or more itinerary days have an invalid or missing date."
            )
        else:
            outside_dates = sorted(
                {d.isoformat() for d in day_dates if d < start_date or d > end_date}
            )
            if outside_dates:
                duration_reasons.append(
                    "Itinerary contains dates outside the trip range: "
                    + ", ".join(outside_dates)
                    + "."
                )
            expected_dates = {
                start_date + timedelta(days=offset)
                for offset in range((end_date - start_date).days + 1)
            }
            actual_dates = set(day_dates)
            if len(day_dates) != len(expected_dates) or actual_dates != expected_dates:
                duration_reasons.append(
                    f"Itinerary covers {len(actual_dates)} distinct days; the trip range requires {len(expected_dates)} days."
                )
            requested_duration = trip_requirements.get("duration_days")
            if requested_duration is not None:
                try:
                    requested_duration = int(requested_duration)
                except (TypeError, ValueError):
                    requested_duration = None
                if requested_duration is not None and requested_duration != len(
                    expected_dates
                ):
                    duration_reasons.append(
                        "Trip duration_days does not match the inclusive start_date/end_date range."
                    )
    checks["duration"] = (
        _check("fail", " ".join(duration_reasons))
        if duration_reasons
        else _check("pass", "Itinerary dates cover the inclusive trip date range.")
    )

    feasibility_reasons: list[str] = []
    status = itinerary.get("status")
    if status in {"infeasible", "invalid_input"}:
        feasibility_reasons.append(f"SchedulingEngine returned status '{status}'.")
    if not isinstance(days, list) or not days:
        feasibility_reasons.append("Itinerary has no scheduled days.")
    elif any(not isinstance(day, dict) or not day.get("items") for day in days):
        feasibility_reasons.append("Itinerary contains a day with no scheduled items.")
    elif len(days) != 1 or days[0].get("day_type") != "day_trip":
        if not any(day.get("hotel_id") for day in days):
            feasibility_reasons.append(
                "Itinerary is missing a required hotel for an overnight trip."
            )
    checks["feasibility"] = (
        _check("fail", " ".join(feasibility_reasons))
        if feasibility_reasons
        else _check("pass", "Schedule has populated days and any required hotel.")
    )

    checks["travelers"] = _check(
        "not_applicable",
        "The current itinerary schema provides no traveller capacity constraint.",
    )

    failed = [name for name, result in checks.items() if result["status"] == "fail"]
    return {
        "passed": not failed,
        "status": "pass" if not failed else "fail",
        "constraints": checks,
        "failed_constraints": failed,
        "reasons": {name: checks[name]["reason"] for name in failed},
    }


@tool
def constraint_validator(
    itinerary: dict, trip_requirements: dict, cost_estimate: dict
) -> dict:
    """Validate itinerary budget, duration, schedule feasibility and explicit capacities."""
    return validate_constraints(itinerary, trip_requirements, cost_estimate)
