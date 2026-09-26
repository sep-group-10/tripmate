"""SchedulingEngine: arranges ranked candidates into a day-by-day itinerary.

Scoped to single-destination trips (see TripMate issue #184 for the
multi-destination night-allocation follow-up — nothing upstream of this tool
can produce more than one destination yet).

Deterministic, no DB access, no LLM calls. Given the same input twice,
produces the same output both times.
"""

from dataclasses import dataclass, field
from datetime import date, time, timedelta
from typing import Any

from langchain_core.tools import tool

from app.services.opening_hours import DayHours, parse_opening_hours
from app.services.tools.scheduling_config import DEFAULT_CONFIG, DayType, ScheduleStatus

_EVENT_CATEGORY = "local_event"
_RESTAURANT_CATEGORY = "restaurant"
_HOTEL_CATEGORY = "hotel"
_ATTRACTION_CATEGORY = "attraction"


@dataclass
class ScheduledItem:
    candidate_id: str
    category: str
    name: str
    start_time: time
    end_time: time
    latitude: Any = None
    longitude: Any = None
    duration_minutes: int | None = None
    opening_hours: Any = None


@dataclass
class DayPlan:
    day_number: int
    date: date
    day_type: DayType
    items: list[ScheduledItem] = field(default_factory=list)
    hotel_id: str | None = None
    hotel_location: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass
class UnscheduledCandidate:
    candidate_id: str
    name: str
    category: str
    reason: str


@dataclass
class ScheduleResult:
    status: ScheduleStatus
    days: list[DayPlan] = field(default_factory=list)
    hotel_by_destination: dict[str, str] = field(default_factory=dict)
    unscheduled: list[UnscheduledCandidate] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _to_serializable_time(value: time) -> str:
    return value.strftime("%H:%M")


def _result_to_dict(result: ScheduleResult) -> dict[str, Any]:
    return {
        "status": result.status.value,
        "days": [
            {
                "day_number": day.day_number,
                "date": day.date.isoformat(),
                "day_type": day.day_type.value,
                "items": [
                    {
                        "candidate_id": item.candidate_id,
                        "category": item.category,
                        "name": item.name,
                        "start_time": _to_serializable_time(item.start_time),
                        "end_time": _to_serializable_time(item.end_time),
                        "latitude": item.latitude,
                        "longitude": item.longitude,
                        "duration_minutes": item.duration_minutes,
                        "opening_hours": item.opening_hours,
                    }
                    for item in day.items
                ],
                "hotel_id": day.hotel_id,
                "hotel_location": day.hotel_location,
                "warnings": day.warnings,
            }
            for day in result.days
        ],
        "hotel_by_destination": result.hotel_by_destination,
        "unscheduled": [
            {
                "candidate_id": item.candidate_id,
                "name": item.name,
                "category": item.category,
                "reason": item.reason,
            }
            for item in result.unscheduled
        ],
        "warnings": result.warnings,
    }


def _minutes_between(start: time, end: time) -> int:
    return (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)


def _add_minutes(start: time, minutes: int) -> time:
    total = start.hour * 60 + start.minute + minutes
    total = min(total, 23 * 60 + 59)
    return time(hour=total // 60, minute=total % 60)


def _validate_input(start_date: date | None, end_date: date | None) -> str | None:
    if start_date is None or end_date is None:
        return "start_date and end_date are required"
    if end_date < start_date:
        return "end_date is before start_date"
    if (end_date - start_date).days + 1 > DEFAULT_CONFIG.max_trip_length_days:
        return f"trip length exceeds the maximum of {DEFAULT_CONFIG.max_trip_length_days} days"
    return None


def _build_day_skeleton(start_date: date, end_date: date) -> list[DayPlan]:
    total_days = (end_date - start_date).days + 1
    days: list[DayPlan] = []

    for offset in range(total_days):
        current_date = start_date + timedelta(days=offset)
        if total_days == 1:
            day_type = DayType.DAY_TRIP
        elif offset == 0:
            day_type = DayType.ARRIVAL
        elif offset == total_days - 1:
            day_type = DayType.DEPARTURE
        else:
            day_type = DayType.FULL

        days.append(
            DayPlan(day_number=offset + 1, date=current_date, day_type=day_type)
        )

    return days


def _activity_window(day: DayPlan) -> tuple[time, time]:
    config = DEFAULT_CONFIG
    return {
        DayType.ARRIVAL: config.arrival_window,
        DayType.FULL: config.full_day_window,
        DayType.TRAVEL: config.travel_day_morning_window,
        DayType.DEPARTURE: config.departure_window,
        DayType.DAY_TRIP: config.day_trip_window,
    }[day.day_type]


def _free_gaps(day: DayPlan, window: tuple[time, time]) -> list[tuple[time, time]]:
    """Free time gaps within window, given items already scheduled on this day."""
    window_start, window_end = window
    occupied = sorted(
        ((item.start_time, item.end_time) for item in day.items),
        key=lambda pair: pair[0],
    )

    gaps: list[tuple[time, time]] = []
    cursor = window_start
    for occ_start, occ_end in occupied:
        if occ_start > window_end:
            break
        if occ_start > cursor:
            gaps.append((cursor, min(occ_start, window_end)))
        cursor = max(cursor, occ_end)

    if cursor < window_end:
        gaps.append((cursor, window_end))

    return [gap for gap in gaps if gap[0] < gap[1]]


def _free_minutes(day: DayPlan, window: tuple[time, time]) -> int:
    return sum(_minutes_between(start, end) for start, end in _free_gaps(day, window))


def _fits_opening_hours(day_hours: DayHours, start: time, end: time) -> bool:
    return day_hours.contains(start, end)


def _schedule_events(
    days: list[DayPlan],
    events: list[dict[str, Any]],
    unscheduled: list[UnscheduledCandidate],
) -> None:
    """Schedule each event on at most one day within its date range.

    Higher-ranked events (they arrive pre-sorted by final_score) win any
    time conflict; a multi-day event is scheduled once, not repeated.
    """
    scheduled_event_ids: set[str] = set()

    for event in events:
        starts_on = event.get("starts_on")
        ends_on = event.get("ends_on")
        start_time_str = event.get("event_start_time")
        end_time_str = event.get("event_end_time")

        if not starts_on or not ends_on or not start_time_str or not end_time_str:
            unscheduled.append(
                UnscheduledCandidate(
                    candidate_id=event["id"],
                    name=event["name"],
                    category=_EVENT_CATEGORY,
                    reason="event is missing date or time information",
                )
            )
            continue

        try:
            range_start = date.fromisoformat(starts_on)
            range_end = date.fromisoformat(ends_on)
            event_start = time.fromisoformat(start_time_str)
            event_end = time.fromisoformat(end_time_str)
        except ValueError:
            unscheduled.append(
                UnscheduledCandidate(
                    candidate_id=event["id"],
                    name=event["name"],
                    category=_EVENT_CATEGORY,
                    reason="event date/time could not be parsed",
                )
            )
            continue

        if range_end < range_start or event_end <= event_start:
            unscheduled.append(
                UnscheduledCandidate(
                    candidate_id=event["id"],
                    name=event["name"],
                    category=_EVENT_CATEGORY,
                    reason="event has an invalid date or time range",
                )
            )
            continue

        candidate_days = [day for day in days if range_start <= day.date <= range_end]
        if not candidate_days:
            unscheduled.append(
                UnscheduledCandidate(
                    candidate_id=event["id"],
                    name=event["name"],
                    category=_EVENT_CATEGORY,
                    reason="event's date range falls outside the trip",
                )
            )
            continue

        placed = False
        for day in candidate_days:
            conflict = any(
                item.start_time < event_end and event_start < item.end_time
                for item in day.items
            )
            if conflict:
                continue

            day.items.append(
                ScheduledItem(
                    candidate_id=event["id"],
                    category=_EVENT_CATEGORY,
                    name=event["name"],
                    start_time=event_start,
                    end_time=event_end,
                    latitude=event.get("latitude"),
                    longitude=event.get("longitude"),
                    duration_minutes=_minutes_between(event_start, event_end),
                )
            )
            scheduled_event_ids.add(event["id"])
            placed = True
            break

        if not placed:
            unscheduled.append(
                UnscheduledCandidate(
                    candidate_id=event["id"],
                    name=event["name"],
                    category=_EVENT_CATEGORY,
                    reason="event overlaps with a higher-priority item on every available day",
                )
            )


def _schedule_meals(days: list[DayPlan], restaurants: list[dict[str, Any]]) -> None:
    """Best-effort lunch (and, on full days, dinner) slot per day.

    Restaurants are consumable, not one-visit-only like attractions: the
    same restaurant may serve different meal slots on different days, but
    never lunch and dinner on the same day.

    If nothing fits, the slot is left empty rather than given to an
    attraction. If an event occupies the normal dinner slot, an earlier
    dinner is attempted instead of dropping the meal.
    """
    config = DEFAULT_CONFIG

    def _pick_restaurant(used_today: set[str]) -> dict[str, Any] | None:
        for restaurant in restaurants:
            if restaurant["id"] not in used_today:
                return restaurant
        return None

    def _slot_is_free(day: DayPlan, slot_start: time, slot_end: time) -> bool:
        return not any(
            item.start_time < slot_end and slot_start < item.end_time
            for item in day.items
        )

    for day in days:
        used_today: set[str] = set()

        if day.day_type == DayType.DEPARTURE:
            meal_slots = []
        elif day.day_type == DayType.ARRIVAL:
            meal_slots = [config.dinner_slot]
        elif day.day_type == DayType.TRAVEL:
            meal_slots = [config.lunch_slot]
        else:
            meal_slots = [config.lunch_slot, config.dinner_slot]

        for slot_start, slot_end in meal_slots:
            candidate_slot = (slot_start, slot_end)

            if not _slot_is_free(day, slot_start, slot_end):
                if candidate_slot == config.dinner_slot:
                    earlier_start = _add_minutes(
                        slot_start, -config.default_meal_duration_minutes
                    )
                    if _slot_is_free(day, earlier_start, slot_start):
                        candidate_slot = (earlier_start, slot_start)
                    else:
                        continue
                else:
                    continue

            restaurant = _pick_restaurant(used_today)
            if restaurant is None:
                continue

            used_today.add(restaurant["id"])
            day.items.append(
                ScheduledItem(
                    candidate_id=restaurant["id"],
                    category=_RESTAURANT_CATEGORY,
                    name=restaurant["name"],
                    start_time=candidate_slot[0],
                    end_time=candidate_slot[1],
                    latitude=restaurant.get("latitude"),
                    longitude=restaurant.get("longitude"),
                    duration_minutes=_minutes_between(
                        candidate_slot[0], candidate_slot[1]
                    ),
                )
            )


def _schedule_attractions(
    days: list[DayPlan],
    attractions: list[dict[str, Any]],
    unscheduled: list[UnscheduledCandidate],
) -> None:
    """Greedy insertion: each attraction, in score order, goes into the
    earliest gap that fits its duration without breaking opening hours, on
    whichever day currently has the most free time."""
    config = DEFAULT_CONFIG

    for attraction in attractions:
        duration_minutes = attraction.get("duration_minutes")
        if duration_minutes is None or duration_minutes <= 0:
            unscheduled.append(
                UnscheduledCandidate(
                    candidate_id=attraction["id"],
                    name=attraction["name"],
                    category=_ATTRACTION_CATEGORY,
                    reason="missing or non-positive duration",
                )
            )
            continue

        parsed_hours = parse_opening_hours(attraction.get("opening_hours"))

        candidate_days = sorted(
            days,
            key=lambda day: _free_minutes(day, _attraction_window_for(day, config)),
            reverse=True,
        )

        placed = False
        for day in candidate_days:
            if day.day_type == DayType.DAY_TRIP:
                window = config.attraction_window
            else:
                window = _attraction_window_for(day, config)

            day_hours = parsed_hours.for_date(day.date)
            if day_hours.is_closed:
                continue

            for gap_start, gap_end in _free_gaps(day, window):
                gap_minutes = _minutes_between(gap_start, gap_end)
                if gap_minutes < duration_minutes:
                    continue

                item_end = _add_minutes(gap_start, duration_minutes)
                if not _fits_opening_hours(day_hours, gap_start, item_end):
                    continue

                day.items.append(
                    ScheduledItem(
                        candidate_id=attraction["id"],
                        category=attraction["category"],
                        name=attraction["name"],
                        start_time=gap_start,
                        end_time=item_end,
                        latitude=attraction.get("latitude"),
                        longitude=attraction.get("longitude"),
                        duration_minutes=duration_minutes,
                        opening_hours=attraction.get("opening_hours"),
                    )
                )
                if parsed_hours.assumed_open:
                    day.warnings.append(
                        f"{attraction['name']}: opening hours unknown, assumed open"
                    )
                placed = True
                break

            if placed:
                break

        if not placed:
            unscheduled.append(
                UnscheduledCandidate(
                    candidate_id=attraction["id"],
                    name=attraction["name"],
                    category=attraction["category"],
                    reason="no day had a fitting, open time slot",
                )
            )


def _attraction_window_for(day: DayPlan, config) -> tuple[time, time]:
    day_window = _activity_window(day)
    return (
        max(day_window[0], config.attraction_window[0]),
        min(day_window[1], config.attraction_window[1]),
    )


def _needs_a_hotel(days: list[DayPlan]) -> bool:
    """A day trip (single DAY_TRIP day) has no night and needs no hotel."""
    return not (len(days) == 1 and days[0].day_type == DayType.DAY_TRIP)


def _assign_hotel(
    days: list[DayPlan],
    hotels: list[dict[str, Any]],
    warnings: list[str],
) -> str | None:
    if not _needs_a_hotel(days):
        return None

    if not hotels:
        warnings.append("no hotel candidate available for this destination")
        return None

    hotel = hotels[0]
    for day in days:
        day.hotel_location = {
            "latitude": hotel.get("latitude"),
            "longitude": hotel.get("longitude"),
        }
        if day.day_type != DayType.DEPARTURE:
            day.hotel_id = hotel["id"]
    return hotel["id"]


def build_schedule(
    candidates: list[dict[str, Any]],
    trip_requirements: dict[str, Any],
) -> dict[str, Any]:
    """Arrange ranked candidates into a day-by-day itinerary.

    candidates: the ranked output of ScoringEngine (score_breakdown/
    final_score already attached), all belonging to a single destination.
    trip_requirements: must contain start_date and end_date (date objects).
    """
    start_date = trip_requirements.get("start_date")
    end_date = trip_requirements.get("end_date")

    validation_error = _validate_input(start_date, end_date)
    if validation_error is not None:
        return _result_to_dict(
            ScheduleResult(
                status=ScheduleStatus.INVALID_INPUT, warnings=[validation_error]
            )
        )

    days = _build_day_skeleton(start_date, end_date)

    events = [c for c in candidates if c["category"] == _EVENT_CATEGORY]
    restaurants = [c for c in candidates if c["category"] == _RESTAURANT_CATEGORY]
    hotels = [c for c in candidates if c["category"] == _HOTEL_CATEGORY]
    attractions = [
        c
        for c in candidates
        if c["category"] not in (_EVENT_CATEGORY, _RESTAURANT_CATEGORY, _HOTEL_CATEGORY)
    ]

    unscheduled: list[UnscheduledCandidate] = []
    warnings: list[str] = []

    _schedule_events(days, events, unscheduled)
    _schedule_meals(days, restaurants)
    _schedule_attractions(days, attractions, unscheduled)

    hotel_id = _assign_hotel(days, hotels, warnings)
    hotel_by_destination = {}
    destination = trip_requirements.get("destination")
    if hotel_id is not None and destination:
        hotel_by_destination[destination] = hotel_id

    has_empty_day = any(not day.items for day in days)
    missing_required_hotel = _needs_a_hotel(days) and hotel_id is None
    has_gap = has_empty_day or missing_required_hotel or bool(unscheduled)
    status = ScheduleStatus.PARTIAL if has_gap else ScheduleStatus.OK

    for day in days:
        if not day.items:
            day.warnings.append("no items scheduled for this day")

    result = ScheduleResult(
        status=status,
        days=days,
        hotel_by_destination=hotel_by_destination,
        unscheduled=unscheduled,
        warnings=warnings,
    )
    return _result_to_dict(result)


@tool
def scheduling_engine(candidates: list[dict], trip_requirements: dict) -> dict:
    """Arrange ranked, single-destination candidates into a day-by-day itinerary.

    Respects opening hours, visit durations, meal slots, and event date
    ranges. Returns a structured schedule with any unscheduled candidates
    and warnings, never crashes on messy input.
    """
    return build_schedule(candidates, trip_requirements)
