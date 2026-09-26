"""Randomised volume testing for SchedulingEngine.

Per the SchedulingEngine plan (#149): generate a large number of randomised,
deliberately messy trip requests and confirm across all of them that nothing
crashes, no time slot is double-booked, no place is scheduled twice, and
day/night counts stay internally consistent.
"""

import random
from datetime import date, timedelta

from app.services.tools.scheduling_engine import build_schedule

_CATEGORIES = ["attraction", "restaurant", "hotel", "local_event"]
_MESSY_OPENING_HOURS_OPTIONS = [
    None,
    {},
    {"monday": "08:00-18:00"},
    {"monday": "closed", "tuesday": "08:00-18:00"},
    {"everyday": "10:00-22:00"},
    {"monday": "not a valid time"},
    {
        day: "08:00-18:00"
        for day in (
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        )
    },
]
_MESSY_DURATIONS = [None, 0, -30, 30, 60, 120, 180, 480]


def _random_candidate(rng: random.Random, index: int) -> dict:
    category = rng.choice(_CATEGORIES)
    candidate = {
        "id": f"c{index}",
        "category": category,
        "name": f"Candidate {index}",
        "description": None,
        "rating": rng.choice([None, 1.0, 3.0, 4.5, 5.0]),
        "entry_fee": rng.choice([None, 0.0, 10.0, 500.0]),
        "opening_hours": rng.choice(_MESSY_OPENING_HOURS_OPTIONS),
        "duration_minutes": rng.choice(_MESSY_DURATIONS)
        if category != "hotel"
        else None,
        "latitude": 7.29 + rng.uniform(-0.1, 0.1),
        "longitude": 80.63 + rng.uniform(-0.1, 0.1),
        "starts_on": None,
        "ends_on": None,
        "event_start_time": None,
        "event_end_time": None,
        "similarity_score": None,
    }

    if category == "local_event":
        trip_start = date(2026, 10, 5)
        offset = rng.randint(-2, 10)
        event_start = trip_start + timedelta(days=offset)
        event_end = event_start + timedelta(days=rng.randint(0, 2))
        candidate["starts_on"] = event_start.isoformat()
        candidate["ends_on"] = event_end.isoformat()
        candidate["event_start_time"] = rng.choice([None, "10:00", "18:00", "19:30"])
        candidate["event_end_time"] = rng.choice([None, "12:00", "21:00", "23:00"])

    return candidate


def _random_trip(rng: random.Random) -> dict:
    trip_length = rng.randint(1, 10)
    start_date = date(2026, 10, 5)
    end_date = start_date + timedelta(days=trip_length - 1)
    return {"destination": "Kandy", "start_date": start_date, "end_date": end_date}


def test_fuzz_never_crashes_and_stays_internally_consistent():
    rng = random.Random(42)

    for trial in range(200):
        candidate_count = rng.randint(0, 30)
        candidates = [_random_candidate(rng, i) for i in range(candidate_count)]
        trip = _random_trip(rng)

        result = build_schedule(candidates, trip)

        assert result["status"] in (
            "ok",
            "partial",
            "infeasible",
            "invalid_input",
        ), trial

        expected_days = (trip["end_date"] - trip["start_date"]).days + 1
        assert len(result["days"]) == expected_days, trial

        for day in result["days"]:
            items = day["items"]

            # No time slot double-booked.
            sorted_items = sorted(items, key=lambda item: item["start_time"])
            for first, second in zip(sorted_items, sorted_items[1:], strict=False):
                assert first["end_time"] <= second["start_time"], (trial, day)

            # No place scheduled twice on the same day.
            candidate_ids = [item["candidate_id"] for item in items]
            assert len(candidate_ids) == len(set(candidate_ids)), (trial, day)

        # No attraction/event scheduled twice across the whole trip.
        all_ids_by_category: dict[str, list[str]] = {}
        for day in result["days"]:
            for item in day["items"]:
                all_ids_by_category.setdefault(item["category"], []).append(
                    item["candidate_id"]
                )
        for category, ids in all_ids_by_category.items():
            if category == "restaurant":
                continue  # restaurants may legitimately repeat across days
            assert len(ids) == len(set(ids)), (trial, category)


def test_fuzz_same_input_twice_is_deterministic():
    rng = random.Random(7)

    for trial in range(50):
        candidate_count = rng.randint(0, 20)
        candidates = [_random_candidate(rng, i) for i in range(candidate_count)]
        trip = _random_trip(rng)

        first = build_schedule(candidates, trip)
        second = build_schedule(candidates, trip)

        assert first == second, trial
