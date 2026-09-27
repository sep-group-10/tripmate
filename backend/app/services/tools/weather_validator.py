"""Validate scheduled itinerary locations against OpenWeather forecasts."""

from __future__ import annotations

import logging
import os
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx
from langchain_core.tools import tool

logger = logging.getLogger(__name__)
_OPENWEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
_REQUEST_TIMEOUT_SECONDS = 5.0


class ForecastUnavailableError(ValueError):
    """Raised when OpenWeather has no forecast for the requested date."""


_OUTDOOR_KEYWORDS = (
    "hike",
    "hiking",
    "trail",
    "trek",
    "beach",
    "park",
    "garden",
    "outdoor",
    "waterfall",
    "mountain",
    "nature",
    "safari",
    "viewpoint",
    "camping",
    "boat",
    "surf",
    "swim",
    "lake",
    "river",
    "wildlife",
    "walk",
)
_INDOOR_KEYWORDS = (
    "indoor",
    "museum",
    "gallery",
    "aquarium",
    "indoor activity",
    "shopping mall",
)
_THUNDERSTORM_CODES = range(200, 300)
_HEAVY_RAIN_CODES = {502, 503, 504, 522, 531}


def _activity_is_weather_sensitive(item: dict[str, Any]) -> bool:
    """Identify activities whose suitability is affected by outdoor weather."""
    searchable = " ".join(
        str(value)
        for key in ("category", "name", "description", "activity_type", "tags")
        if (value := item.get(key)) is not None
    ).casefold()
    if any(keyword in searchable for keyword in _INDOOR_KEYWORDS):
        return False
    if any(keyword in searchable for keyword in _OUTDOOR_KEYWORDS):
        return True
    return str(item.get("category", "")).casefold() == "attraction"


def _parse_forecast_for_date(
    payload: dict[str, Any], forecast_date: str
) -> dict[str, Any]:
    entries = payload.get("list")
    if not isinstance(entries, list):
        raise ValueError("OpenWeather response did not contain forecast entries")

    timezone_offset = int((payload.get("city") or {}).get("timezone", 0) or 0)

    def local_forecast_date(entry: dict[str, Any]) -> str:
        timestamp = entry.get("dt")
        if timestamp is not None:
            local_time = datetime.fromtimestamp(
                float(timestamp), timezone.utc
            ) + timedelta(seconds=timezone_offset)
            return local_time.date().isoformat()
        return str(entry.get("dt_txt", ""))[:10]

    matching = [
        entry
        for entry in entries
        if isinstance(entry, dict) and local_forecast_date(entry) == forecast_date
    ]
    if not matching:
        raise ForecastUnavailableError(
            "OpenWeather forecast is unavailable for itinerary date"
        )

    probabilities = [float(entry.get("pop", 0) or 0) for entry in matching]
    rain_amounts = [
        float((entry.get("rain") or {}).get("3h", 0) or 0)
        for entry in matching
        if isinstance(entry.get("rain") or {}, dict)
    ]
    weather = next(
        (
            condition
            for entry in matching
            for condition in entry.get("weather", [])
            if isinstance(condition, dict)
        ),
        {},
    )
    main = next(
        (
            entry.get("main")
            for entry in matching
            if isinstance(entry.get("main"), dict)
        ),
        {},
    )
    weather_code = weather.get("id")
    max_rain_mm = max(rain_amounts, default=0.0)
    precipitation_probability = max(probabilities, default=0.0)

    if (
        weather_code in _THUNDERSTORM_CODES
        or weather_code in _HEAVY_RAIN_CODES
        or max_rain_mm >= 10
    ):
        status = "problem"
    elif precipitation_probability >= 0.4 or max_rain_mm >= 1:
        status = "warning"
    else:
        status = "ok"

    return {
        "status": status,
        "description": weather.get("description"),
        "weather_code": weather_code,
        "temperature_c": main.get("temp"),
        "precipitation_probability": precipitation_probability,
        "rain_mm": round(sum(rain_amounts), 2),
    }


def _fetch_forecast(
    forecast_date: str,
    latitude: float,
    longitude: float,
    api_key: str,
) -> dict[str, Any]:
    response = httpx.get(
        _OPENWEATHER_FORECAST_URL,
        params={
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": "metric",
        },
        timeout=_REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("OpenWeather returned an invalid response")
    return _parse_forecast_for_date(payload, forecast_date)


def _coordinate(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if -90 <= number <= 90 else None


def _longitude(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if -180 <= number <= 180 else None


def validate_schedule_weather(
    schedule: dict[str, Any],
    *,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Return per-day, per-location weather assessments for a schedule."""
    key = api_key if api_key is not None else os.getenv("OPENWEATHER_API_KEY")
    cache: dict[tuple[str, float, float], dict[str, Any]] = {}
    result_days: list[dict[str, Any]] = []
    overall_status = "ok"

    days = schedule.get("days") if isinstance(schedule, dict) else None
    if not isinstance(days, list):
        return {
            "status": "could_not_check",
            "days": [],
            "warnings": ["Schedule does not contain a valid days list"],
        }

    for day in days:
        if not isinstance(day, dict):
            continue
        day_date = str(day.get("date", ""))
        try:
            date.fromisoformat(day_date)
        except ValueError:
            day_date = ""
        items = day.get("items") if isinstance(day.get("items"), list) else []
        grouped: dict[tuple[float, float] | None, list[dict[str, Any]]] = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            lat = _coordinate(item.get("latitude"))
            lon = _longitude(item.get("longitude"))
            if lat is None or lon is None:
                hotel_location = day.get("hotel_location") or {}
                lat = (
                    _coordinate(hotel_location.get("latitude"))
                    if isinstance(hotel_location, dict)
                    else None
                )
                lon = (
                    _longitude(hotel_location.get("longitude"))
                    if isinstance(hotel_location, dict)
                    else None
                )
            location = (lat, lon) if lat is not None and lon is not None else None
            grouped.setdefault(location, []).append(item)

        locations: list[dict[str, Any]] = []
        day_status = "ok"
        for location, location_items in grouped.items():
            if location is None or not day_date or not key:
                status = "could_not_check"
                forecast: dict[str, Any] = {}
                reason = (
                    "Missing valid itinerary date or coordinates"
                    if location is None or not day_date
                    else "OPENWEATHER_API_KEY is not configured"
                )
                if not key:
                    logger.warning(
                        "Weather validation skipped: OPENWEATHER_API_KEY is not configured"
                    )
            else:
                cache_key = (day_date, round(location[0], 5), round(location[1], 5))
                if cache_key not in cache:
                    try:
                        cache[cache_key] = _fetch_forecast(
                            day_date, location[0], location[1], key
                        )
                    except ForecastUnavailableError as exc:
                        logger.warning(
                            "OpenWeather forecast unavailable for %s at %s,%s",
                            day_date,
                            location[0],
                            location[1],
                        )
                        cache[cache_key] = {
                            "status": "could_not_check",
                            "error": str(exc),
                        }
                    except Exception as exc:  # weather must never block planning
                        logger.warning(
                            "OpenWeather lookup failed for %s at %s,%s (%s)",
                            day_date,
                            location[0],
                            location[1],
                            type(exc).__name__,
                        )
                        cache[cache_key] = {
                            "status": "could_not_check",
                            "error": "Weather data is temporarily unavailable",
                        }
                forecast = cache[cache_key]
                status = forecast["status"]
                reason = forecast.get("error")

            day_status = _worst_status(day_status, status)
            activity_results = []
            for item in location_items:
                sensitive = _activity_is_weather_sensitive(item)
                activity_results.append(
                    {
                        "candidate_id": item.get("candidate_id"),
                        "name": item.get("name"),
                        "category": item.get("category"),
                        "weather_sensitive": sensitive,
                        "weather_status": status if sensitive else "not_applicable",
                    }
                )
            location_result = {
                "latitude": location[0] if location is not None else None,
                "longitude": location[1] if location is not None else None,
                "status": status,
                "weather": forecast,
                "activities": activity_results,
            }
            if reason:
                location_result["reason"] = reason
            locations.append(location_result)

        overall_status = _worst_status(overall_status, day_status)
        result_days.append(
            {
                "day_number": day.get("day_number"),
                "date": day.get("date"),
                "status": day_status,
                "locations": locations,
            }
        )

    warnings = [
        f"Weather check for {day['date']} returned {location['status']}"
        for day in result_days
        for location in day["locations"]
        if location["status"] in {"warning", "problem", "could_not_check"}
    ]
    return {"status": overall_status, "days": result_days, "warnings": warnings}


def _worst_status(first: str, second: str) -> str:
    order = {"ok": 0, "warning": 1, "problem": 2, "could_not_check": 3}
    return second if order[second] > order[first] else first


@tool
def weather_validator(schedule: dict) -> dict:
    """Check each scheduled day and location against OpenWeather forecasts.

    Pass the dictionary returned by SchedulingEngine (or RouteOptimizer).
    """
    return validate_schedule_weather(schedule)
