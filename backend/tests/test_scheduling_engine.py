from datetime import date

from app.services.tools.scheduling_config import DayType, ScheduleStatus
from app.services.tools.scheduling_engine import build_schedule

_OPEN_ALL_WEEK = {
    "monday": "08:00-18:00",
    "tuesday": "08:00-18:00",
    "wednesday": "08:00-18:00",
    "thursday": "08:00-18:00",
    "friday": "08:00-18:00",
    "saturday": "08:00-18:00",
    "sunday": "08:00-18:00",
}

_RESTAURANT_HOURS = {
    "monday": "10:00-22:00",
    "tuesday": "10:00-22:00",
    "wednesday": "10:00-22:00",
    "thursday": "10:00-22:00",
    "friday": "10:00-22:00",
    "saturday": "10:00-22:00",
    "sunday": "10:00-22:00",
}


def _attraction(id_, **overrides):
    base = {
        "id": id_,
        "category": "attraction",
        "name": f"Attraction {id_}",
        "description": None,
        "rating": 4.0,
        "entry_fee": 5.0,
        "opening_hours": dict(_OPEN_ALL_WEEK),
        "duration_minutes": 120,
        "latitude": 7.29,
        "longitude": 80.63,
        "starts_on": None,
        "ends_on": None,
        "event_start_time": None,
        "event_end_time": None,
        "similarity_score": None,
    }
    base.update(overrides)
    return base


def _restaurant(id_, **overrides):
    base = {
        "id": id_,
        "category": "restaurant",
        "name": f"Restaurant {id_}",
        "description": None,
        "rating": 4.0,
        "entry_fee": 10.0,
        "opening_hours": dict(_RESTAURANT_HOURS),
        "duration_minutes": 60,
        "latitude": 7.29,
        "longitude": 80.63,
        "starts_on": None,
        "ends_on": None,
        "event_start_time": None,
        "event_end_time": None,
        "similarity_score": None,
    }
    base.update(overrides)
    return base


def _hotel(id_, **overrides):
    base = {
        "id": id_,
        "category": "hotel",
        "name": f"Hotel {id_}",
        "description": None,
        "rating": 4.0,
        "entry_fee": 50.0,
        "opening_hours": None,
        "duration_minutes": None,
        "latitude": 7.29,
        "longitude": 80.63,
        "starts_on": None,
        "ends_on": None,
        "event_start_time": None,
        "event_end_time": None,
        "similarity_score": None,
    }
    base.update(overrides)
    return base


def _event(id_, starts_on, ends_on, start_time="18:00", end_time="21:00", **overrides):
    base = {
        "id": id_,
        "category": "local_event",
        "name": f"Event {id_}",
        "description": None,
        "rating": 4.5,
        "entry_fee": 0.0,
        "opening_hours": None,
        "duration_minutes": 180,
        "latitude": 7.29,
        "longitude": 80.63,
        "starts_on": starts_on,
        "ends_on": ends_on,
        "event_start_time": start_time,
        "event_end_time": end_time,
        "similarity_score": None,
    }
    base.update(overrides)
    return base


_TRIP_3_DAYS = {
    "destination": "Kandy",
    "start_date": date(2026, 10, 5),
    "end_date": date(2026, 10, 7),
}


def test_day_types_assigned_correctly_for_multi_day_trip():
    result = build_schedule([], _TRIP_3_DAYS)

    day_types = [day["day_type"] for day in result["days"]]
    assert day_types == [DayType.ARRIVAL, DayType.FULL, DayType.DEPARTURE]


def test_day_trip_is_single_day_type_day_trip():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 5),
    }
    result = build_schedule([], trip)

    assert len(result["days"]) == 1
    assert result["days"][0]["day_type"] == DayType.DAY_TRIP


def test_place_closed_on_monday_not_scheduled_on_monday():
    monday_trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),  # a Monday
        "end_date": date(2026, 10, 5),
    }
    closed_monday_hours = {
        day: hours for day, hours in _OPEN_ALL_WEEK.items() if day != "monday"
    }
    attraction = _attraction("a1", opening_hours=closed_monday_hours)

    result = build_schedule([attraction], monday_trip)

    assert result["days"][0]["items"] == []
    assert any(u["candidate_id"] == "a1" for u in result["unscheduled"])


def test_visit_must_fit_before_closing_not_just_start_before_closing():
    # Open 08:00-18:00, arrival day window starts at 14:00, a 5-hour visit
    # starting at 14:00 would end at 19:00 -- past closing.
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 6),
    }
    attraction = _attraction("a1", duration_minutes=300)

    result = build_schedule([attraction], trip)

    arrival_day = result["days"][0]
    assert not any(item["candidate_id"] == "a1" for item in arrival_day["items"])


def test_attractions_scheduled_without_overpacking_a_day():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 5),
    }
    attractions = [_attraction(f"a{i}", duration_minutes=180) for i in range(5)]

    result = build_schedule(attractions, trip)

    day = result["days"][0]
    total_scheduled_minutes = sum(
        _minutes(item["start_time"], item["end_time"]) for item in day["items"]
    )
    assert total_scheduled_minutes <= _minutes("09:00", "21:00")
    assert len(result["unscheduled"]) > 0


def test_lunch_slot_filled_with_restaurant_on_full_day():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 7),
    }
    restaurant = _restaurant("r1")

    result = build_schedule([restaurant], trip)

    full_day = result["days"][1]
    assert any(item["category"] == "restaurant" for item in full_day["items"])


def test_dinner_slot_filled_on_full_day():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 7),
    }
    restaurants = [_restaurant("r1"), _restaurant("r2")]

    result = build_schedule(restaurants, trip)

    full_day = result["days"][1]
    restaurant_items = [
        item for item in full_day["items"] if item["category"] == "restaurant"
    ]
    assert len(restaurant_items) == 2


def test_no_restaurant_available_leaves_meal_slot_empty_not_filled_with_attraction():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 7),
    }
    attraction = _attraction("a1", duration_minutes=60)

    result = build_schedule([attraction], trip)

    full_day = result["days"][1]
    lunch_start, lunch_end = "12:30", "13:30"
    overlapping_lunch = [
        item
        for item in full_day["items"]
        if item["start_time"] < lunch_end and lunch_start < item["end_time"]
    ]
    assert not any(item["category"] == "attraction" for item in overlapping_lunch)


def test_evening_event_in_dinner_slot_pushes_dinner_earlier_not_dropped():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 7),
    }
    event = _event(
        "e1", "2026-10-06", "2026-10-06", start_time="19:00", end_time="21:30"
    )
    restaurant = _restaurant("r1")

    result = build_schedule([event, restaurant], trip)

    full_day = result["days"][1]
    restaurant_items = [
        item for item in full_day["items"] if item["category"] == "restaurant"
    ]
    assert len(restaurant_items) == 1
    assert restaurant_items[0]["end_time"] <= "19:00"


def test_event_only_scheduled_within_its_date_range():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 7),
    }
    event = _event("e1", "2026-10-06", "2026-10-06")

    result = build_schedule([event], trip)

    assert not any(item["candidate_id"] == "e1" for item in result["days"][0]["items"])
    assert any(item["candidate_id"] == "e1" for item in result["days"][1]["items"])
    assert not any(item["candidate_id"] == "e1" for item in result["days"][2]["items"])


def test_multiday_event_scheduled_once_not_every_day():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 7),
    }
    event = _event("e1", "2026-10-05", "2026-10-07")

    result = build_schedule([event], trip)

    total_occurrences = sum(
        1
        for day in result["days"]
        for item in day["items"]
        if item["candidate_id"] == "e1"
    )
    assert total_occurrences == 1


def test_overlapping_events_keeps_higher_priority_drops_the_other():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 5),
    }
    high_priority = _event(
        "e1", "2026-10-05", "2026-10-05", start_time="18:00", end_time="21:00"
    )
    low_priority = _event(
        "e2", "2026-10-05", "2026-10-05", start_time="18:30", end_time="20:30"
    )

    result = build_schedule([high_priority, low_priority], trip)

    scheduled_ids = {item["candidate_id"] for item in result["days"][0]["items"]}
    assert "e1" in scheduled_ids
    assert "e2" not in scheduled_ids
    assert any(u["candidate_id"] == "e2" for u in result["unscheduled"])


def test_event_missing_time_fields_left_unscheduled_with_reason():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 5),
    }
    event = _event("e1", "2026-10-05", "2026-10-05", start_time=None, end_time=None)

    result = build_schedule([event], trip)

    assert result["unscheduled"][0]["candidate_id"] == "e1"
    assert "missing" in result["unscheduled"][0]["reason"]


def test_hotel_assigned_to_every_night_not_departure_day():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 7),
    }
    hotel = _hotel("h1")

    result = build_schedule([hotel], trip)

    assert result["days"][0]["hotel_id"] == "h1"
    assert result["days"][1]["hotel_id"] == "h1"
    assert result["days"][2]["hotel_id"] is None
    assert result["hotel_by_destination"]["Kandy"] == "h1"


def test_no_hotel_candidate_produces_warning_not_failure():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 7),
    }

    result = build_schedule([], trip)

    assert any("hotel" in warning for warning in result["warnings"])
    assert result["status"] != ScheduleStatus.INFEASIBLE


def test_day_trip_needs_no_hotel_and_produces_no_hotel_warning():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 5),
    }
    attraction = _attraction("a1", duration_minutes=120)

    result = build_schedule([attraction], trip)

    assert not any("hotel" in warning for warning in result["warnings"])
    assert result["days"][0]["hotel_id"] is None


def test_zero_duration_candidate_skipped_not_stalling():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 5),
    }
    attraction = _attraction("a1", duration_minutes=0)

    result = build_schedule([attraction], trip)

    assert any(u["candidate_id"] == "a1" for u in result["unscheduled"])
    assert "duration" in result["unscheduled"][0]["reason"]


def test_negative_duration_candidate_skipped():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 5),
    }
    attraction = _attraction("a1", duration_minutes=-30)

    result = build_schedule([attraction], trip)

    assert any(u["candidate_id"] == "a1" for u in result["unscheduled"])


def test_empty_candidate_list_returns_valid_empty_itinerary():
    result = build_schedule([], _TRIP_3_DAYS)

    assert result["status"] in (ScheduleStatus.PARTIAL, ScheduleStatus.OK)
    assert len(result["days"]) == 3
    assert result["unscheduled"] == []


def test_end_date_before_start_date_is_invalid_input():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 7),
        "end_date": date(2026, 10, 5),
    }

    result = build_schedule([], trip)

    assert result["status"] == ScheduleStatus.INVALID_INPUT
    assert result["days"] == []


def test_unreasonably_long_trip_is_invalid_input():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 12, 31),
    }

    result = build_schedule([], trip)

    assert result["status"] == ScheduleStatus.INVALID_INPUT


def test_missing_dates_is_invalid_input():
    result = build_schedule([], {"destination": "Kandy"})

    assert result["status"] == ScheduleStatus.INVALID_INPUT


def test_fewer_candidates_than_days_never_repeats_a_place():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 9),
    }
    attraction = _attraction("a1", duration_minutes=120)

    result = build_schedule([attraction], trip)

    occurrences = sum(
        1
        for day in result["days"]
        for item in day["items"]
        if item["candidate_id"] == "a1"
    )
    assert occurrences == 1


def test_all_candidates_closed_on_available_day_produces_empty_day_not_crash():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 5),
    }
    closed_hours = {day: "closed" for day in _OPEN_ALL_WEEK}
    attraction = _attraction("a1", opening_hours=closed_hours)

    result = build_schedule([attraction], trip)

    assert result["days"][0]["items"] == []
    assert "no items scheduled for this day" in result["days"][0]["warnings"]


def test_unrecognisable_opening_hours_assumed_open_and_flagged():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 5),
    }
    attraction = _attraction("a1", opening_hours={"monday": "sometime probably"})

    result = build_schedule([attraction], trip)

    assert any(item["candidate_id"] == "a1" for item in result["days"][0]["items"])
    assert any("assumed open" in warning for warning in result["days"][0]["warnings"])


def test_running_same_input_twice_produces_identical_output():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 7),
    }
    candidates = [
        _attraction("a1"),
        _attraction("a2"),
        _restaurant("r1"),
        _hotel("h1"),
        _event("e1", "2026-10-06", "2026-10-06"),
    ]

    first = build_schedule(candidates, trip)
    second = build_schedule(candidates, trip)

    assert first == second


def test_ok_status_when_every_day_has_items_and_hotel_assigned():
    trip = {
        "destination": "Kandy",
        "start_date": date(2026, 10, 5),
        "end_date": date(2026, 10, 5),
    }
    attraction = _attraction("a1", duration_minutes=120)
    hotel = _hotel("h1")

    result = build_schedule([attraction, hotel], trip)

    assert result["status"] == ScheduleStatus.OK


def _minutes(start_str: str, end_str: str) -> int:
    start_h, start_m = map(int, start_str.split(":"))
    end_h, end_m = map(int, end_str.split(":"))
    return (end_h * 60 + end_m) - (start_h * 60 + start_m)
