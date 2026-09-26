"""Configuration constants for SchedulingEngine.

All time-window boundaries live here rather than scattered through the
scheduling logic, so they can be tuned without hunting through code.
"""

from dataclasses import dataclass
from datetime import time
from enum import StrEnum


class DayType(StrEnum):
    ARRIVAL = "arrival"
    FULL = "full"
    TRAVEL = "travel"
    DEPARTURE = "departure"
    DAY_TRIP = "day_trip"


class ScheduleStatus(StrEnum):
    OK = "ok"
    PARTIAL = "partial"
    INFEASIBLE = "infeasible"
    INVALID_INPUT = "invalid_input"


@dataclass(frozen=True)
class SchedulingConfig:
    # Activity windows per day type. (start, end) as time-of-day.
    arrival_window: tuple[time, time] = (time(14, 0), time(21, 0))
    full_day_window: tuple[time, time] = (time(9, 0), time(21, 0))
    travel_day_morning_window: tuple[time, time] = (time(9, 0), time(12, 0))
    travel_day_evening_window: tuple[time, time] = (time(17, 0), time(21, 0))
    departure_window: tuple[time, time] = (time(8, 0), time(12, 0))
    day_trip_window: tuple[time, time] = (time(9, 0), time(21, 0))

    # Attractions are scheduled within this narrower window; events may run
    # later into the evening (concerts/cultural shows are normally after dark).
    attraction_window: tuple[time, time] = (time(9, 0), time(18, 0))

    lunch_slot: tuple[time, time] = (time(12, 30), time(13, 30))
    dinner_slot: tuple[time, time] = (time(19, 0), time(20, 0))
    default_meal_duration_minutes: int = 60

    max_trip_length_days: int = 60


DEFAULT_CONFIG = SchedulingConfig()
