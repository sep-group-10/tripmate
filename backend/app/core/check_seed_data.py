"""Read-only data-quality report for the tourism tables.

    python -m app.core.check_seed_data          # database report
    python -m app.core.check_seed_data --urls   # also verify the Commons photo URLs

Reports (active rows only):
  - places more than 30 km from their destination
  - active destinations without an active hotel
  - active destinations with fewer than 3 restaurants open for dinner
  - active events that have already ended
  - prices far outside the normal range

With --urls, every URL in seed_data/photo_credits.py is fetched (network needed)
and must load as an image from upload.wikimedia.org with an allowed licence.

Exits with status 1 if anything is reported, so it can gate CI or a deploy.
"""

import math
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone

from app.core.database import SessionLocal
from app.core.seed_data.photo_credits import PHOTO_CREDITS
from app.models.attraction import Attraction
from app.models.destination import Destination
from app.models.hotel import Hotel
from app.models.local_event import LocalEvent
from app.models.restaurant import Restaurant
from app.services.opening_hours import parse_opening_hours
from app.services.tools.scheduling_config import DEFAULT_CONFIG

MAX_DISTANCE_KM = 30.0
MIN_DINNER_RESTAURANTS = 3

# (min, max) plausible values, in the same currency the seed uses (USD scale).
PRICE_RANGES = {
    "hotel price_per_night": (10, 1000),
    "restaurant avg_meal_cost": (1, 100),
    "attraction entry_fee": (0, 50),
    "event entry_fee": (0, 100),
}

_ALLOWED_LICENSE = re.compile(r"^(CC0|CC BY(-SA)? \d|Public domain)", re.IGNORECASE)
_USER_AGENT = "TripMateSeedCheck/1.0 (student project)"

_PLACE_MODELS = (
    ("attraction", Attraction),
    ("hotel", Hotel),
    ("restaurant", Restaurant),
    ("event", LocalEvent),
)


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    lat1, lon1, lat2, lon2 = (math.radians(float(v)) for v in (lat1, lon1, lat2, lon2))
    a = (
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    )
    return 2 * 6371.0 * math.asin(math.sqrt(a))


def _active_destinations(db) -> list[Destination]:
    return (
        db.query(Destination)
        .filter(Destination.is_active.is_(True))
        .order_by(Destination.name)
        .all()
    )


def find_far_places(db, max_km: float = MAX_DISTANCE_KM) -> list[dict]:
    far = []
    for destination in _active_destinations(db):
        for kind, model in _PLACE_MODELS:
            rows = (
                db.query(model)
                .filter(
                    model.destination_id == destination.id,
                    model.is_active.is_(True),
                )
                .all()
            )
            for row in rows:
                km = haversine_km(
                    destination.latitude,
                    destination.longitude,
                    row.latitude,
                    row.longitude,
                )
                if km > max_km:
                    far.append(
                        {
                            "kind": kind,
                            "name": row.name,
                            "destination": destination.name,
                            "km": round(km, 1),
                        }
                    )
    return sorted(far, key=lambda item: -item["km"])


def find_destinations_without_hotel(db) -> list[str]:
    return [
        destination.name
        for destination in _active_destinations(db)
        if not db.query(Hotel)
        .filter(Hotel.destination_id == destination.id, Hotel.is_active.is_(True))
        .count()
    ]


def covers_dinner(operating_hours) -> bool:
    """Open for the whole dinner slot on every day of the week. Missing or
    unparseable hours do not count: the planner would merely *assume* open."""
    parsed = parse_opening_hours(operating_hours)
    if parsed.assumed_open:
        return False
    return all(
        day.contains(*DEFAULT_CONFIG.dinner_slot) for day in parsed.days.values()
    )


def find_destinations_short_on_dinner(
    db, minimum: int = MIN_DINNER_RESTAURANTS
) -> list[dict]:
    short = []
    for destination in _active_destinations(db):
        restaurants = (
            db.query(Restaurant)
            .filter(
                Restaurant.destination_id == destination.id,
                Restaurant.is_active.is_(True),
            )
            .all()
        )
        count = sum(1 for r in restaurants if covers_dinner(r.operating_hours))
        if count < minimum:
            short.append(
                {
                    "destination": destination.name,
                    "dinner_restaurants": count,
                    "active_restaurants": len(restaurants),
                }
            )
    return short


def find_past_events(db, today: date | None = None) -> list[dict]:
    today = today or datetime.now(timezone.utc).date()
    rows = (
        db.query(LocalEvent, Destination.name)
        .join(Destination, Destination.id == LocalEvent.destination_id)
        .filter(LocalEvent.is_active.is_(True), LocalEvent.ends_on < today)
        .order_by(Destination.name, LocalEvent.starts_on)
        .all()
    )
    return [
        {"name": event.name, "destination": destination, "ended": event.ends_on}
        for event, destination in rows
    ]


def find_price_outliers(db) -> list[dict]:
    checks = (
        ("hotel price_per_night", Hotel, "price_per_night"),
        ("restaurant avg_meal_cost", Restaurant, "avg_meal_cost"),
        ("attraction entry_fee", Attraction, "entry_fee"),
        ("event entry_fee", LocalEvent, "entry_fee"),
    )
    outliers = []
    for label, model, column in checks:
        low, high = PRICE_RANGES[label]
        rows = (
            db.query(model, Destination.name)
            .join(Destination, Destination.id == model.destination_id)
            .filter(model.is_active.is_(True))
            .all()
        )
        for row, destination in rows:
            value = getattr(row, column)
            if value < low or value > high:
                outliers.append(
                    {
                        "field": label,
                        "name": row.name,
                        "destination": destination,
                        "value": value,
                        "expected": f"{low}-{high}",
                    }
                )
    return outliers


def run_checks(db, today: date | None = None) -> dict[str, list]:
    return {
        "places_over_30_km": find_far_places(db),
        "destinations_without_active_hotel": find_destinations_without_hotel(db),
        "destinations_with_few_dinner_restaurants": (
            find_destinations_short_on_dinner(db)
        ),
        "past_events": find_past_events(db, today),
        "price_outliers": find_price_outliers(db),
    }


_TITLES = {
    "places_over_30_km": f"Active places more than {MAX_DISTANCE_KM:g} km from their destination",
    "destinations_without_active_hotel": "Active destinations without an active hotel",
    "destinations_with_few_dinner_restaurants": (
        f"Active destinations with fewer than {MIN_DINNER_RESTAURANTS} restaurants "
        "open for dinner (19:00-20:00, every day)"
    ),
    "past_events": "Active events that have already ended",
    "price_outliers": "Prices far outside the normal range",
}


def _format(item) -> str:
    if isinstance(item, str):
        return item
    return ", ".join(f"{key}={value}" for key, value in item.items())


def check_photo_urls(pause: float = 1.0) -> list[str]:
    """Fetch every credited photo URL; returns a list of problems."""
    problems = []
    for credit in PHOTO_CREDITS:
        label = credit["used_for"]
        url = credit["url"]
        if not url.startswith("https://upload.wikimedia.org/"):
            problems.append(f"{label}: not an upload.wikimedia.org URL")
        if not _ALLOWED_LICENSE.match(credit["license"]):
            problems.append(f"{label}: licence {credit['license']!r} not allowed")
        if not (credit["author"] and credit["source"]):
            problems.append(f"{label}: missing author or source")

        request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        for attempt in range(5):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    content_type = response.headers.get("Content-Type", "")
                    response.read()
                if not content_type.startswith("image/"):
                    problems.append(f"{label}: content type {content_type!r}")
                break
            except urllib.error.HTTPError as error:
                if error.code == 429 and attempt < 4:
                    time.sleep(15 * (attempt + 1))
                    continue
                problems.append(f"{label}: HTTP {error.code}")
                break
            except OSError as error:
                problems.append(f"{label}: {error}")
                break
        time.sleep(pause)
    return problems


def main() -> int:
    db = SessionLocal()
    try:
        results = run_checks(db)
    finally:
        db.close()

    issues = 0
    for key, title in _TITLES.items():
        items = results[key]
        issues += len(items)
        print(f"\n{title}: {'OK' if not items else len(items)}")
        for item in items:
            print(f"  - {_format(item)}")

    if "--urls" in sys.argv[1:]:
        problems = check_photo_urls()
        issues += len(problems)
        print(
            f"\nCommons photo URLs ({len(PHOTO_CREDITS)} checked): "
            f"{'OK' if not problems else len(problems)}"
        )
        for problem in problems:
            print(f"  - {problem}")

    print(f"\n{issues} issue(s) found." if issues else "\nNo issues found.")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
