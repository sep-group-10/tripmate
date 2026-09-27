import json

import httpx

from app.services.tools import weather_validator as weather_module
from app.services.tools.weather_validator import (
    validate_schedule_weather,
    weather_validator,
)


def _schedule(*days):
    return {"status": "ok", "days": list(days)}


def _day(day_date="2026-10-05", *items, day_number=1):
    return {"date": day_date, "day_number": day_number, "items": list(items)}


def _item(name="Lake walk", category="attraction", lat=7.2906, lon=80.6337):
    return {
        "candidate_id": name.lower().replace(" ", "-"),
        "name": name,
        "category": category,
        "latitude": lat,
        "longitude": lon,
    }


def _response(*, code=800, pop=0.1, rain=0.0):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "list": [
                    {
                        "dt_txt": f"{forecast_date} 12:00:00",
                        "pop": pop,
                        "rain": {"3h": rain},
                        "weather": [{"id": code, "description": "test weather"}],
                        "main": {"temp": 25.0},
                    }
                    for forecast_date in ("2026-10-05", "2026-10-06")
                ]
            }

    return Response()


def _mock_api(monkeypatch, *, response=None, error=None):
    calls = []

    def get(url, *, params, timeout):
        calls.append((url, params, timeout))
        if error:
            raise error
        return response or _response()

    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")
    monkeypatch.setattr(weather_module.httpx, "get", get)
    return calls


def test_ok_weather(monkeypatch):
    _mock_api(monkeypatch, response=_response(code=800, pop=0.1))

    result = validate_schedule_weather(_schedule(_day("2026-10-05", _item())))

    assert result["status"] == "ok"
    assert result["days"][0]["locations"][0]["weather"]["temperature_c"] == 25.0


def test_warning_weather_for_meaningful_rain_probability(monkeypatch):
    _mock_api(monkeypatch, response=_response(code=500, pop=0.6, rain=0.4))

    result = validate_schedule_weather(_schedule(_day("2026-10-05", _item())))

    assert result["status"] == "warning"
    assert result["days"][0]["locations"][0]["status"] == "warning"


def test_problem_weather_for_thunderstorm(monkeypatch):
    _mock_api(monkeypatch, response=_response(code=202))

    result = validate_schedule_weather(_schedule(_day("2026-10-05", _item())))

    assert result["status"] == "problem"


def test_forecast_unavailable_reports_specific_reason(monkeypatch):
    _mock_api(monkeypatch, response=_response())

    result = validate_schedule_weather(_schedule(_day("2026-10-10", _item())))

    location = result["days"][0]["locations"][0]

    assert location["status"] == "could_not_check"
    assert (
        location["reason"] == "OpenWeather forecast is unavailable for itinerary date"
    )


def test_weather_sensitive_outdoor_activity_is_flagged(monkeypatch):
    _mock_api(monkeypatch)

    result = validate_schedule_weather(
        _schedule(_day("2026-10-05", _item("Hiking trail")))
    )

    activity = result["days"][0]["locations"][0]["activities"][0]
    assert activity["weather_sensitive"] is True


def test_indoor_activity_is_not_flagged_as_weather_sensitive(monkeypatch):
    _mock_api(monkeypatch, response=_response(code=202))

    result = validate_schedule_weather(
        _schedule(_day("2026-10-05", _item("Kandy Art Museum", "attraction")))
    )

    activity = result["days"][0]["locations"][0]["activities"][0]
    assert activity["weather_sensitive"] is False
    assert activity["weather_status"] == "not_applicable"


def test_multiple_days_and_locations_are_checked(monkeypatch):
    calls = _mock_api(monkeypatch)
    schedule = _schedule(
        _day(
            "2026-10-05", _item("Park visit"), _item("Garden", lat=6.9271, lon=79.8612)
        ),
        _day("2026-10-06", _item("Beach visit", lat=6.0535, lon=80.2210), day_number=2),
    )

    result = validate_schedule_weather(schedule)

    assert len(result["days"]) == 2
    assert sum(len(day["locations"]) for day in result["days"]) == 3
    assert len(calls) == 3


def test_same_date_and_coordinates_use_only_one_api_request(monkeypatch):
    calls = _mock_api(monkeypatch)
    schedule = _schedule(
        _day("2026-10-05", _item("Lake walk"), _item("Temple visit", "attraction"))
    )

    result = validate_schedule_weather(schedule)

    assert len(calls) == 1
    assert len(result["days"][0]["locations"]) == 1
    assert len(result["days"][0]["locations"][0]["activities"]) == 2


def test_api_failure_returns_safe_result_without_raising(monkeypatch):
    _mock_api(monkeypatch, error=httpx.ConnectError("offline"))

    result = validate_schedule_weather(_schedule(_day("2026-10-05", _item())))

    assert result["status"] == "could_not_check"
    assert result["days"][0]["locations"][0]["status"] == "could_not_check"


def test_missing_api_key_returns_safe_result(monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    calls = []
    monkeypatch.setattr(
        weather_module.httpx, "get", lambda *args, **kwargs: calls.append(args)
    )

    result = validate_schedule_weather(_schedule(_day("2026-10-05", _item())))

    assert result["status"] == "could_not_check"
    assert calls == []


def test_result_is_json_and_langchain_tool_serializable(monkeypatch):
    _mock_api(monkeypatch)
    schedule = _schedule(_day("2026-10-05", _item()))

    direct_result = weather_validator.invoke({"schedule": schedule})

    assert json.loads(json.dumps(direct_result)) == direct_result
