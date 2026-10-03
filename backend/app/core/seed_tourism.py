"""Idempotent tourism seed.

The data lives in app/core/seed_data (one module per destination). Every run
inserts what is missing and updates what already exists, so corrections to the
data apply on re-run. Nothing is ever deleted: stale rows are deactivated
(is_active=false) instead.

Matching keys: destinations by name, places by (destination, name), transport
rates by (transport_type, region).
"""

from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func

from app.core.database import SessionLocal
from app.core.seed_data import DESTINATION_SEEDS, TRANSPORT_RATES
from app.core.seed_data.photos import (
    ATTRACTION_PHOTOS,
    EVENT_PHOTOS,
    HOTEL_PHOTOS,
    PHOTO_CDN,
    RESTAURANT_PHOTOS,
)
from app.models.attraction import Attraction
from app.models.destination import Destination
from app.models.hotel import Hotel
from app.models.local_event import LocalEvent
from app.models.restaurant import Restaurant
from app.models.transport_rate import TransportRate


def _dec(value) -> Decimal:
    return Decimal(str(value))


def _photo_values(photos: dict[str, str], name: str) -> dict:
    """photo_urls to write for a place, or nothing when the map has no entry
    (so photos uploaded through the admin pages are not wiped)."""
    key = photos.get(name)
    return {"photo_urls": [f"{PHOTO_CDN}/{key}"]} if key else {}


def _upsert(db, model, match: dict, values: dict, deactivate_extras: bool = False):
    """Update the row matching ``match`` or insert it; returns the row.

    If several rows match (duplicates from earlier manual data entry), the
    first one -- preferring an active row -- is updated and, when
    ``deactivate_extras`` is set, the others are deactivated, never deleted.
    """
    query = db.query(model).filter_by(**match)
    if hasattr(model, "is_active"):
        query = query.order_by(model.is_active.desc())
    rows = query.order_by(model.id).all()

    if not rows:
        row = model(**match, **values)
        db.add(row)
        db.flush()
        return row

    row = rows[0]
    for field, value in values.items():
        setattr(row, field, value)
    if deactivate_extras:
        for extra in rows[1:]:
            extra.is_active = False
    return row


def seed_destinations(db):
    destinations = {}
    for data in DESTINATION_SEEDS:
        values = {
            "description": data["description"],
            "country": data["country"],
            "region": data["region"],
            "latitude": _dec(data["latitude"]),
            "longitude": _dec(data["longitude"]),
            "is_active": data["is_active"],
        }
        existing = (
            db.query(Destination).filter(Destination.name == data["name"]).first()
        )
        if existing is None and "id" in data:
            values["id"] = data["id"]
        destinations[data["name"]] = _upsert(
            db, Destination, {"name": data["name"]}, values
        )
    db.commit()
    return destinations


def seed_transport_rates(db):
    for rate in TRANSPORT_RATES:
        _upsert(
            db,
            TransportRate,
            {"transport_type": rate["transport_type"], "region": rate["region"]},
            {"cost_per_km": rate["cost_per_km"], "base_fare": rate["base_fare"]},
        )
    db.commit()


def _seed_attractions(db, destination, data):
    for name in data.get("deactivate_attractions", []):
        db.query(Attraction).filter(
            Attraction.destination_id == destination.id,
            func.lower(Attraction.name) == name.lower(),
        ).update({"is_active": False}, synchronize_session=False)

    for item in data["attractions"]:
        _upsert(
            db,
            Attraction,
            {"destination_id": destination.id, "name": item["name"]},
            {
                "description": item["description"],
                "latitude": _dec(item["latitude"]),
                "longitude": _dec(item["longitude"]),
                "entry_fee": _dec(item["entry_fee"]),
                "duration_hours": _dec(item["duration_hours"]),
                "rating": _dec(item["rating"]),
                "opening_hours": item["opening_hours"],
                "is_active": True,
                **_photo_values(ATTRACTION_PHOTOS, item["name"]),
            },
            deactivate_extras=True,
        )


def _seed_hotels(db, destination, data):
    for item in data["hotels"]:
        _upsert(
            db,
            Hotel,
            {"destination_id": destination.id, "name": item["name"]},
            {
                "description": item["description"],
                "latitude": _dec(item["latitude"]),
                "longitude": _dec(item["longitude"]),
                "price_per_night": _dec(item["price_per_night"]),
                "facilities": item["facilities"],
                "rating": _dec(item["rating"]),
                "is_active": True,
                **_photo_values(HOTEL_PHOTOS, item["name"]),
            },
            deactivate_extras=True,
        )


def _seed_restaurants(db, destination, data):
    for item in data["restaurants"]:
        _upsert(
            db,
            Restaurant,
            {"destination_id": destination.id, "name": item["name"]},
            {
                "description": item["description"],
                "latitude": _dec(item["latitude"]),
                "longitude": _dec(item["longitude"]),
                "cuisine_type": item["cuisine_type"],
                "avg_meal_cost": _dec(item["avg_meal_cost"]),
                "operating_hours": item["operating_hours"],
                "rating": _dec(item["rating"]),
                "is_active": True,
                **_photo_values(RESTAURANT_PHOTOS, item["name"]),
            },
            deactivate_extras=True,
        )


def _duration_hours(start_time: str, end_time: str) -> Decimal:
    start = time.fromisoformat(start_time)
    end = time.fromisoformat(end_time)
    minutes = (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)
    return (Decimal(minutes) / Decimal(60)).quantize(Decimal("0.01"))


def _seed_events(db, destination, data, today: date):
    for item in data["events"]:
        starts_on = today + timedelta(days=item["days_ahead"])
        ends_on = starts_on + timedelta(days=item["duration_days"] - 1)
        _upsert(
            db,
            LocalEvent,
            {"destination_id": destination.id, "name": item["name"]},
            {
                "description": item["description"],
                "latitude": _dec(item["latitude"]),
                "longitude": _dec(item["longitude"]),
                "entry_fee": _dec(item["entry_fee"]),
                "rating": _dec(item["rating"]),
                "duration_hours": _duration_hours(item["start_time"], item["end_time"]),
                "event_schedule": {
                    "date": starts_on.isoformat(),
                    "start_time": item["start_time"],
                    "end_time": item["end_time"],
                },
                "starts_on": starts_on,
                "ends_on": ends_on,
                "is_active": True,
                **_photo_values(EVENT_PHOTOS, item["name"]),
            },
            deactivate_extras=True,
        )


def seed_tourism(db=None, today: date | None = None):
    """Seed destinations, transport rates and all places.

    ``today`` anchors the event dates (defaults to the current date) so a
    re-run always produces future events. Pass ``db`` to use an existing
    session (it is committed); otherwise a session is opened and closed here.
    """
    today = today or datetime.now(timezone.utc).date()
    owns_session = db is None
    if owns_session:
        db = SessionLocal()

    try:
        destinations = seed_destinations(db)
        seed_transport_rates(db)

        for data in DESTINATION_SEEDS:
            destination = destinations[data["name"]]
            _seed_attractions(db, destination, data)
            _seed_hotels(db, destination, data)
            _seed_restaurants(db, destination, data)
            _seed_events(db, destination, data, today)

        db.commit()
        print("Tourism seed data applied successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        if owns_session:
            db.close()


if __name__ == "__main__":
    seed_tourism()
