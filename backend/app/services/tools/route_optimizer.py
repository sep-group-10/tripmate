"""Reorder attraction stops within fixed-commitment blocks of a scheduled itinerary."""

from __future__ import annotations

import copy
import itertools
import logging
from datetime import date, datetime, time, timedelta
from typing import Any

from langchain_core.tools import tool

from app.services import routing
from app.services.routing import TravelEstimate
from app.services.opening_hours import parse_opening_hours
from app.services.tools.scheduling_config import DEFAULT_CONFIG, DayType

logger = logging.getLogger(__name__)
_ATTRACTION = "attraction"


def _clock(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def _clock_str(value: time) -> str:
    return value.strftime("%H:%M")


def _coordinates(item: dict[str, Any] | None) -> tuple[float, float] | None:
    if not item:
        return None
    lat, lng = item.get("latitude"), item.get("longitude")
    if lat is None or lng is None:
        return None
    try:
        return float(lat), float(lng)
    except (TypeError, ValueError):
        return None


def _day_window(day: dict[str, Any]) -> tuple[time, time]:
    day_type = DayType(day["day_type"])
    windows = {
        DayType.ARRIVAL: DEFAULT_CONFIG.arrival_window,
        DayType.FULL: DEFAULT_CONFIG.full_day_window,
        DayType.TRAVEL: DEFAULT_CONFIG.travel_day_morning_window,
        DayType.DEPARTURE: DEFAULT_CONFIG.departure_window,
        DayType.DAY_TRIP: DEFAULT_CONFIG.day_trip_window,
    }
    start, end = windows[day_type]
    return max(start, DEFAULT_CONFIG.attraction_window[0]), min(
        end, DEFAULT_CONFIG.attraction_window[1]
    )


def _travel(origin: tuple[float, float], dest: tuple[float, float]) -> TravelEstimate:
    return routing.estimate_travel_time(origin[0], origin[1], dest[0], dest[1])


def _open_at(item: dict[str, Any], day_date: date, start: time, end: time) -> bool:
    parsed = parse_opening_hours(item.get("opening_hours"))
    return parsed.for_date(day_date).contains(start, end)


def _optimise_block(
    day: dict[str, Any],
    block: list[dict[str, Any]],
    previous_anchor: dict[str, Any] | None,
    window_start: time,
    window_end: time,
    next_anchor: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], bool, str | None]:
    if len(block) < 2:
        return block, False, None
    if len(block) > 4:
        return (
            block,
            False,
            "More than four attractions in this block; route order unchanged",
        )

    for item in block:
        if _coordinates(item) is None:
            return (
                block,
                False,
                f"{item.get('name', item.get('candidate_id', 'Attraction'))}: missing coordinates; route order unchanged",
            )

    try:
        day_date = date.fromisoformat(day["date"])
        origin = _coordinates(previous_anchor)
        if previous_anchor is None:
            origin = _coordinates(day.get("hotel_location"))
        original = block
        if origin is None and day.get("day_type") != DayType.DAY_TRIP.value:
            # The hotel location may not have been available in older schedules.
            origin = _coordinates(original[0])

        best = block
        best_distance = float("inf")
        best_times: dict[str, tuple[time, time]] = {}
        for order in itertools.permutations(block):
            cursor_dt = datetime.combine(day_date, window_start)
            distance = 0.0
            previous = origin
            times: dict[str, tuple[time, time]] = {}
            feasible = True
            for item in order:
                current = _coordinates(item)
                assert current is not None
                if previous is not None:
                    leg = _travel(previous, current)
                    distance += leg.distance_km
                    cursor_dt += timedelta(minutes=leg.duration_minutes)
                duration = item.get("duration_minutes")
                if not isinstance(duration, int) or duration <= 0:
                    duration = int(
                        (
                            _clock(item["end_time"]) - _clock(item["start_time"])
                        ).total_seconds()
                        // 60
                    )
                end_dt = cursor_dt + timedelta(minutes=duration)
                start_time, end_time = cursor_dt.time(), end_dt.time()
                if (
                    end_dt.date() != day_date
                    or end_time > window_end
                    or not _open_at(item, day_date, start_time, end_time)
                ):
                    feasible = False
                    break
                times[item["candidate_id"]] = (start_time, end_time)
                cursor_dt = end_dt
                previous = current
            if feasible and next_anchor is not None:
                destination = _coordinates(next_anchor)
                if destination is not None:
                    assert previous is not None
                    final_leg = _travel(previous, destination)
                    cursor_dt += timedelta(minutes=final_leg.duration_minutes)
                    feasible = cursor_dt <= datetime.combine(day_date, window_end)
            if feasible and distance < best_distance - 1e-9:
                best = list(order)
                best_distance = distance
                best_times = times

        if not best_times or [i["candidate_id"] for i in best] == [
            i["candidate_id"] for i in block
        ]:
            return block, False, None
        updated = []
        for item in best:
            changed = dict(item)
            start, end = best_times[item["candidate_id"]]
            changed["start_time"] = _clock_str(start)
            changed["end_time"] = _clock_str(end)
            updated.append(changed)
        return (
            updated,
            [i["candidate_id"] for i in updated] != [i["candidate_id"] for i in block],
            None,
        )
    except Exception:
        logger.exception(
            "Route optimization failed for day %s; preserving original block",
            day.get("day_number"),
        )
        return block, False, "Routing failed; original attraction order kept"


def optimize_routes(schedule: dict[str, Any]) -> dict[str, Any]:
    """Optimize attraction ordering without moving fixed-time items."""
    result = copy.deepcopy(schedule)
    days = result.get("days")
    if not isinstance(days, list):
        return result

    for day in days:
        items = day.get("items")
        if not isinstance(items, list):
            day["route_optimization"] = {"reordered": False, "warning": None}
            continue

        sorted_items = sorted(items, key=lambda item: item.get("start_time", "00:00"))
        rebuilt: list[dict[str, Any]] = []
        day_reordered = False
        warnings: list[str] = []
        pending: list[dict[str, Any]] = []
        previous_anchor: dict[str, Any] | None = None
        window_start, window_end = _day_window(day)

        def flush(next_anchor: dict[str, Any] | None) -> None:
            nonlocal pending, previous_anchor, day_reordered
            block_start = window_start
            block_end = window_end
            if previous_anchor is not None:
                block_start = max(block_start, _clock(previous_anchor["end_time"]))
            if next_anchor is not None:
                block_end = min(block_end, _clock(next_anchor["start_time"]))
            optimized, reordered, warning = _optimise_block(
                day, pending, previous_anchor, block_start, block_end, next_anchor
            )
            rebuilt.extend(optimized)
            day_reordered = day_reordered or reordered
            if warning:
                warnings.append(warning)
            if next_anchor is not None:
                rebuilt.append(next_anchor)
                previous_anchor = next_anchor
            pending = []

        for item in sorted_items:
            if item.get("category") == _ATTRACTION:
                pending.append(item)
            else:
                flush(item)
        flush(None)
        day["items"] = rebuilt
        day["route_optimization"] = {
            "reordered": day_reordered,
            "warning": "; ".join(warnings) if warnings else None,
        }
    return result


@tool
def route_optimizer(schedule: dict) -> dict:
    """Reorder attraction stops within each day while preserving fixed commitments."""
    return optimize_routes(schedule)
