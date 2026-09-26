"""Parser for admin-entered opening_hours / operating_hours JSONB data.

Real seed data uses lowercase full day names mapped to a single "HH:MM-HH:MM"
24-hour string (see app/core/seed_tourism.py). Admin-entered data will not
always be this clean, so this parser also tolerates:
  - abbreviated day names ("mon", "tue", ...)
  - 12-hour time with am/pm ("9:00am-6:00pm")
  - a single "everyday"/"daily" entry applying to all seven days
  - split hours for a day (a list of "HH:MM-HH:MM" strings, e.g. lunch break)
  - an explicit "closed" value for a day

If a value can't be understood at all, the safe default is to assume the
place is open all day and flag it — silently excluding a place because of a
parsing quirk is worse than occasionally including one that shouldn't be.
"""

import re
from dataclasses import dataclass, field
from datetime import date, time

_DAY_NAMES = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)

_DAY_ALIASES = {
    "mon": "monday",
    "tue": "tuesday",
    "tues": "tuesday",
    "wed": "wednesday",
    "thu": "thursday",
    "thur": "thursday",
    "thurs": "thursday",
    "fri": "friday",
    "sat": "saturday",
    "sun": "sunday",
    **{day: day for day in _DAY_NAMES},
}

_EVERYDAY_ALIASES = {"everyday", "every day", "daily", "all"}
_CLOSED_ALIASES = {"closed", "close", "none"}

_TIME_RANGE_RE = re.compile(
    r"^\s*(\d{1,2}(?::\d{2})?\s*[ap]?m?)\s*-\s*(\d{1,2}(?::\d{2})?\s*[ap]?m?)\s*$",
    re.IGNORECASE,
)


@dataclass
class DayHours:
    """Resolved open intervals for one day. Empty ranges means closed."""

    ranges: list[tuple[time, time]] = field(default_factory=list)

    @property
    def is_closed(self) -> bool:
        return not self.ranges

    def contains(self, start: time, end: time) -> bool:
        """Whether the entire [start, end) window fits inside a single range."""
        return any(
            range_start <= start and end <= range_end
            for range_start, range_end in self.ranges
        )


@dataclass
class ParsedOpeningHours:
    days: dict[str, DayHours]
    assumed_open: bool = False
    parse_warning: str | None = None

    def for_date(self, on_date: date) -> DayHours:
        day_name = _DAY_NAMES[on_date.weekday()]
        return self.days[day_name]


def _parse_time_token(token: str) -> time:
    token = token.strip().lower()
    meridiem = None
    if token.endswith(("am", "pm")):
        meridiem = token[-2:]
        token = token[:-2].strip()

    if ":" in token:
        hour_str, minute_str = token.split(":", 1)
    else:
        hour_str, minute_str = token, "0"

    hour = int(hour_str)
    minute = int(minute_str)

    if meridiem == "pm" and hour != 12:
        hour += 12
    elif meridiem == "am" and hour == 12:
        hour = 0

    return time(hour=hour % 24, minute=minute)


def _parse_range(range_str: str) -> tuple[time, time]:
    match = _TIME_RANGE_RE.match(range_str)
    if not match:
        raise ValueError(f"Unrecognised time range: {range_str!r}")
    start_token, end_token = match.groups()
    return _parse_time_token(start_token), _parse_time_token(end_token)


def _parse_day_value(value) -> DayHours:
    if value is None:
        return DayHours(ranges=[])

    if isinstance(value, str):
        if value.strip().lower() in _CLOSED_ALIASES:
            return DayHours(ranges=[])
        return DayHours(ranges=[_parse_range(value)])

    if isinstance(value, list):
        ranges = [_parse_range(item) for item in value]
        return DayHours(ranges=ranges)

    raise ValueError(f"Unrecognised opening_hours value: {value!r}")


def _assume_open_all_day(warning: str) -> ParsedOpeningHours:
    all_day = DayHours(ranges=[(time(0, 0), time(23, 59))])
    return ParsedOpeningHours(
        days=dict.fromkeys(_DAY_NAMES, all_day),
        assumed_open=True,
        parse_warning=warning,
    )


def parse_opening_hours(raw: dict | None) -> ParsedOpeningHours:
    """Parse an opening_hours/operating_hours JSONB value.

    Never raises. Anything that can't be understood falls back to
    "assume open all day", flagged via assumed_open/parse_warning.
    """
    if raw is None:
        return _assume_open_all_day("opening_hours is missing")

    if not isinstance(raw, dict) or not raw:
        return _assume_open_all_day("opening_hours is not a usable object")

    normalized_keys = {key.strip().lower() for key in raw}
    if normalized_keys & _EVERYDAY_ALIASES:
        everyday_key = next(
            key for key in raw if key.strip().lower() in _EVERYDAY_ALIASES
        )
        try:
            hours = _parse_day_value(raw[everyday_key])
        except ValueError as exc:
            return _assume_open_all_day(str(exc))
        return ParsedOpeningHours(days=dict.fromkeys(_DAY_NAMES, hours))

    days: dict[str, DayHours] = {}
    for raw_key, raw_value in raw.items():
        day_name = _DAY_ALIASES.get(raw_key.strip().lower())
        if day_name is None:
            continue
        try:
            days[day_name] = _parse_day_value(raw_value)
        except ValueError as exc:
            return _assume_open_all_day(str(exc))

    if not days:
        return _assume_open_all_day("no recognisable day keys in opening_hours")

    # A day simply absent from an otherwise-valid schedule is treated as
    # closed (e.g. "closed Mondays" represented by omitting monday), not as
    # unparseable data -- the "assume open" fallback is reserved for values
    # that genuinely couldn't be understood at all.
    missing_days = set(_DAY_NAMES) - days.keys()
    for day_name in missing_days:
        days[day_name] = DayHours(ranges=[])

    return ParsedOpeningHours(days=days)
