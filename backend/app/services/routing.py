"""Shared travel-time estimation service.

Used by SchedulingEngine to sequence days, and intended to be shared by
RouteOptimizer for ordering stops within a day.

No real routing API is wired in yet — see the follow-up infra issue for
enabling Google's Routes API. Every result here is a straight-line estimate,
tagged accordingly so callers (and the Critic) can tell an estimate from a
real measurement.
"""

import math
from dataclasses import dataclass
from decimal import Decimal

ROAD_WINDING_FACTOR = 1.3
AVERAGE_ROAD_SPEED_KMH = 35
MINUTES_ROUNDING = 15
EARTH_RADIUS_KM = 6371.0


@dataclass(frozen=True)
class TravelEstimate:
    duration_minutes: int
    distance_km: float
    travel_source: str  # "routes_api" (not yet implemented) or "estimate"


def _haversine_km(
    origin_lat: Decimal | float,
    origin_lng: Decimal | float,
    dest_lat: Decimal | float,
    dest_lng: Decimal | float,
) -> float:
    lat1, lng1, lat2, lng2 = (
        math.radians(float(origin_lat)),
        math.radians(float(origin_lng)),
        math.radians(float(dest_lat)),
        math.radians(float(dest_lng)),
    )
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    )
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def _round_to_nearest(minutes: float, step: int) -> int:
    return int(round(minutes / step) * step)


_cache: dict[tuple, TravelEstimate] = {}


def estimate_travel_time(
    origin_lat: Decimal | float,
    origin_lng: Decimal | float,
    dest_lat: Decimal | float,
    dest_lng: Decimal | float,
) -> TravelEstimate:
    """Estimate travel time between two coordinates.

    Currently always a straight-line estimate (haversine distance x a road
    winding factor, at an average road speed), since no real routing API is
    configured. Known limitation: underestimates hill-country roads, where a
    straight-line distance is a poor proxy for actual travel time.
    """
    cache_key = (
        round(float(origin_lat), 6),
        round(float(origin_lng), 6),
        round(float(dest_lat), 6),
        round(float(dest_lng), 6),
    )
    if cache_key in _cache:
        return _cache[cache_key]

    distance_km = _haversine_km(origin_lat, origin_lng, dest_lat, dest_lng)
    road_distance_km = distance_km * ROAD_WINDING_FACTOR
    duration_minutes_raw = (road_distance_km / AVERAGE_ROAD_SPEED_KMH) * 60
    duration_minutes = _round_to_nearest(duration_minutes_raw, MINUTES_ROUNDING)

    estimate = TravelEstimate(
        duration_minutes=duration_minutes,
        distance_km=distance_km,
        travel_source="estimate",
    )
    _cache[cache_key] = estimate
    return estimate


def clear_cache() -> None:
    """Clear the in-process travel-time cache. Test-only."""
    _cache.clear()
