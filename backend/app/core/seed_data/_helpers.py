DAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)


def hours(default: str, **overrides: str) -> dict[str, str]:
    """Weekly hours dict: ``default`` ("HH:MM-HH:MM") every day, with
    per-day overrides such as ``sunday="closed"``."""
    schedule = dict.fromkeys(DAYS, default)
    schedule.update(overrides)
    return schedule
