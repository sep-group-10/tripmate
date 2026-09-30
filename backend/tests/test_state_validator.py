from datetime import date
from decimal import Decimal

import pytest

from app.schemas.agent_session import AgentSession
from app.services.langgraph.state_validator import validate_planning_state


def _schedule(*, days=None):
    return {
        "status": "ok",
        "days": [
            {
                "day_number": 1,
                "date": "2026-10-05",
                "day_type": "day_trip",
                "items": [
                    {
                        "candidate_id": "place-1",
                        "category": "attraction",
                        "name": "Temple of the Tooth",
                        "start_time": "09:00",
                        "end_time": "10:00",
                        "latitude": 7.29,
                        "longitude": 80.63,
                        "duration_minutes": 60,
                        "opening_hours": None,
                    }
                ],
                "hotel_id": None,
                "hotel_location": None,
                "warnings": [],
            }
        ]
        if days is None
        else days,
        "hotel_by_destination": {},
        "unscheduled": [],
        "warnings": [],
    }


def _session(*, requirements=None, schedule=None, tool_results=None):
    trip_requirements = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 5),
        "budget": Decimal("50000"),
        "travelers": 2,
    }
    if requirements:
        trip_requirements.update(requirements)
    results = (
        [{"tool": "scheduling_engine", "result": schedule or _schedule()}]
        if tool_results is None
        else tool_results
    )
    return AgentSession(
        goal="Plan a trip to Kandy",
        trip_requirements=trip_requirements,
        tool_results=results,
    )


def _assert_check_fails(result, check_name):
    assert result["status"] == "fail"
    assert result["passed"] is False
    assert check_name in result["failed_checks"]
    assert result["checks"][check_name]["reasons"]


def test_valid_state_passes():
    result = validate_planning_state(_session())

    assert result["status"] == "pass"
    assert result["passed"] is True
    assert result["failed_checks"] == []


@pytest.mark.parametrize(
    "requirements, expected",
    [
        ({"destination": None}, "destination"),
        ({"start_date": None}, "start_date"),
        ({"end_date": None}, "end_date"),
        ({"budget": None}, "budget"),
        ({"travelers": None}, "travelers"),
    ],
)
def test_missing_required_trip_requirement_fails(requirements, expected):
    result = validate_planning_state(_session(requirements=requirements))

    _assert_check_fails(result, "trip_requirements")
    assert any(
        expected in reason
        for reason in result["checks"]["trip_requirements"]["reasons"]
    )


def test_missing_tool_results_fails():
    session = _session(tool_results=[])

    _assert_check_fails(validate_planning_state(session), "tool_results")


def test_null_tool_result_fails():
    session = _session(tool_results=[{"tool": "scheduling_engine", "result": None}])

    _assert_check_fails(validate_planning_state(session), "tool_results")


def test_malformed_tool_result_fails():
    session = _session(
        tool_results=[{"tool": "candidate_retriever", "result": {"items": []}}]
    )

    _assert_check_fails(validate_planning_state(session), "tool_results")


def test_unknown_tool_result_fails():
    session = _session(tool_results=[{"tool": "unknown_tool", "result": []}])

    _assert_check_fails(validate_planning_state(session), "tool_results")


def test_missing_scheduling_days_fails():
    schedule = _schedule()
    del schedule["days"]
    session = _session(schedule=schedule)

    result = validate_planning_state(session)

    _assert_check_fails(result, "tool_results")
    _assert_check_fails(result, "itinerary")


def test_empty_days_fails():
    session = _session(schedule=_schedule(days=[]))

    result = validate_planning_state(session)

    _assert_check_fails(result, "itinerary")
    _assert_check_fails(result, "itinerary_items")


def test_empty_itinerary_items_fails():
    schedule = _schedule()
    schedule["days"][0]["items"] = []

    _assert_check_fails(
        validate_planning_state(_session(schedule=schedule)), "itinerary_items"
    )


def test_malformed_itinerary_item_fails():
    schedule = _schedule()
    schedule["days"][0]["items"][0].pop("name")

    result = validate_planning_state(_session(schedule=schedule))

    _assert_check_fails(result, "itinerary_items")
    assert any(
        "name" in reason for reason in result["checks"]["itinerary_items"]["reasons"]
    )


def test_missing_applicable_coordinates_and_location_fails():
    schedule = _schedule()
    schedule["days"][0]["items"][0].pop("latitude")
    schedule["days"][0]["items"][0].pop("longitude")

    result = validate_planning_state(_session(schedule=schedule))

    _assert_check_fails(result, "itinerary_items")
    assert any(
        "coordinates" in reason
        for reason in result["checks"]["itinerary_items"]["reasons"]
    )


def test_valid_scheduling_result_passes():
    result = validate_planning_state(_session(schedule=_schedule()))

    assert result["checks"]["itinerary"]["status"] == "pass"
    assert result["checks"]["itinerary_items"]["status"] == "pass"
