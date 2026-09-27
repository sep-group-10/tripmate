from datetime import date
from decimal import Decimal

from app.services.tools.constraint_validator import (
    constraint_validator,
    validate_constraints,
)


def _inputs(*, cost_max=Decimal("900"), itinerary=None):
    return {
        "itinerary": itinerary
        or {
            "status": "ok",
            "days": [
                {"date": "2026-10-05", "items": [{"category": "attraction"}]},
                {"date": "2026-10-06", "items": [{"category": "restaurant"}]},
            ],
            "unscheduled": [],
        },
        "trip_requirements": {
            "budget": Decimal("1000"),
            "start_date": date(2026, 10, 5),
            "end_date": date(2026, 10, 6),
            "duration_days": 2,
            "travelers": 2,
        },
        "cost_estimate": {"total": {"min": Decimal("700"), "max": cost_max}},
    }


def test_valid_plan_passes():
    result = validate_constraints(**_inputs())

    assert result["passed"] is True
    assert result["status"] == "pass"
    assert result["failed_constraints"] == []
    assert result["constraints"]["travelers"]["status"] == "not_applicable"


def test_over_budget_plan_fails_using_decimal_maximum():
    result = validate_constraints(**_inputs(cost_max=Decimal("1000.01")))

    assert result["passed"] is False
    assert result["failed_constraints"] == ["budget"]
    assert "exceeds" in result["reasons"]["budget"]


def test_wrong_or_out_of_range_duration_fails():
    inputs = _inputs()
    inputs["itinerary"]["days"].append(
        {"date": "2026-10-07", "items": [{"category": "attraction"}]}
    )

    result = validate_constraints(**inputs)

    assert "duration" in result["failed_constraints"]
    assert "outside the trip range" in result["reasons"]["duration"]


def test_basic_infeasibility_fails():
    inputs = _inputs()
    inputs["itinerary"]["status"] = "partial"
    inputs["itinerary"]["unscheduled"] = [{"candidate_id": "required-1"}]

    result = validate_constraints(**inputs)

    assert "feasibility" in result["failed_constraints"]
    assert "partial" in result["reasons"]["feasibility"]


def test_result_names_failed_constraint_and_reason():
    result = constraint_validator.invoke(_inputs(cost_max=Decimal("1001")))

    assert result["failed_constraints"] == ["budget"]
    assert result["reasons"]["budget"]
    assert result["constraints"]["budget"]["status"] == "fail"
