from datetime import date, time

from app.services.opening_hours import parse_opening_hours

_MONDAY = date(2026, 10, 5)
_SUNDAY = date(2026, 10, 11)


def test_parses_real_seed_data_format():
    raw = {
        "monday": "08:00-18:00",
        "tuesday": "08:00-18:00",
        "wednesday": "08:00-18:00",
        "thursday": "08:00-18:00",
        "friday": "08:00-18:00",
        "saturday": "08:00-18:00",
        "sunday": "08:00-18:00",
    }

    parsed = parse_opening_hours(raw)

    assert not parsed.assumed_open
    hours = parsed.for_date(_MONDAY)
    assert hours.contains(time(9, 0), time(11, 0))
    assert not hours.is_closed


def test_visit_must_fit_entirely_inside_window_not_just_start_time():
    raw = {day: "08:00-18:00" for day in _all_days()}
    parsed = parse_opening_hours(raw)
    hours = parsed.for_date(_MONDAY)

    # Starts before close, but doesn't fit within it.
    assert not hours.contains(time(17, 30), time(19, 30))
    # Fully fits.
    assert hours.contains(time(16, 0), time(18, 0))


def test_abbreviated_day_names():
    raw = {"mon": "09:00-17:00", "tue": "09:00-17:00"}
    parsed = parse_opening_hours(raw)

    assert parsed.days["monday"].contains(time(10, 0), time(11, 0))
    assert parsed.days["tuesday"].contains(time(10, 0), time(11, 0))


def test_twelve_hour_time_format():
    raw = {day: "9:00am-6:00pm" for day in _all_days()}
    parsed = parse_opening_hours(raw)

    hours = parsed.for_date(_MONDAY)
    assert hours.contains(time(10, 0), time(11, 0))
    assert not hours.contains(time(18, 30), time(19, 0))


def test_everyday_single_entry():
    raw = {"everyday": "10:00-22:00"}
    parsed = parse_opening_hours(raw)

    for day_name in parsed.days:
        assert parsed.days[day_name].contains(time(12, 0), time(13, 0))


def test_split_hours_for_lunch_break():
    raw = {"monday": ["08:00-12:00", "13:00-18:00"]}
    parsed = parse_opening_hours(raw)

    hours = parsed.days["monday"]
    assert hours.contains(time(9, 0), time(10, 0))
    assert hours.contains(time(14, 0), time(15, 0))
    # Doesn't fit any single range, even though it's "within business hours".
    assert not hours.contains(time(11, 30), time(13, 30))


def test_explicit_closed_value():
    raw = {day: "08:00-18:00" for day in _all_days() if day != "monday"}
    raw["monday"] = "closed"
    parsed = parse_opening_hours(raw)

    assert parsed.days["monday"].is_closed
    assert not parsed.days["monday"].contains(time(10, 0), time(11, 0))


def test_missing_value_treated_as_closed():
    raw = {"monday": None}
    parsed = parse_opening_hours(raw)

    assert parsed.days["monday"].is_closed


def test_unparseable_value_assumes_open_and_flags():
    raw = {"monday": "sometime in the afternoon probably"}
    parsed = parse_opening_hours(raw)

    assert parsed.assumed_open
    assert parsed.parse_warning is not None
    assert parsed.days["monday"].contains(time(10, 0), time(11, 0))


def test_none_input_assumes_open_and_flags():
    parsed = parse_opening_hours(None)

    assert parsed.assumed_open
    assert parsed.parse_warning is not None
    assert parsed.for_date(_SUNDAY).contains(time(23, 0), time(23, 30))


def test_empty_dict_assumes_open_and_flags():
    parsed = parse_opening_hours({})

    assert parsed.assumed_open
    assert parsed.parse_warning is not None


def test_day_absent_from_otherwise_valid_schedule_treated_as_closed():
    raw = {"monday": "08:00-18:00"}
    parsed = parse_opening_hours(raw)

    assert not parsed.assumed_open
    assert parsed.days["tuesday"].is_closed
    assert not parsed.days["tuesday"].contains(time(10, 0), time(11, 0))


def _all_days():
    return [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
