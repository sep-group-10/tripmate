"""Candidate retrieval tool for the TripMate planning graph."""

from datetime import time
from typing import Any

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.attraction import Attraction
from app.models.destination import Destination
from app.models.hotel import Hotel
from app.models.local_event import LocalEvent
from app.models.restaurant import Restaurant

_DEFAULT_EVENT_DURATION_MINUTES = 120
_DEFAULT_RESTAURANT_DURATION_MINUTES = 60


def _serialize_attraction(row: Attraction) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "category": "attraction",
        "name": row.name,
        "description": row.description,
        "rating": float(row.rating) if row.rating else 3.0,
        "entry_fee": float(row.entry_fee) if row.entry_fee else 0.0,
        "opening_hours": row.opening_hours,
        # duration_hours is NOT NULL (enforced by migration), so no fallback
        # is needed. Converted to minutes so SchedulingEngine works in
        # consistent minutes throughout.
        "duration_minutes": int(row.duration_hours * 60),
        "latitude": float(row.latitude),
        "longitude": float(row.longitude),
        "starts_on": None,
        "ends_on": None,
        "event_start_time": None,
        "event_end_time": None,
        "similarity_score": None,
    }


def _serialize_restaurant(row: Restaurant) -> dict[str, Any]:
    # avg_meal_cost and operating_hours are the correct DB column names for
    # restaurants. They are normalized here to entry_fee and opening_hours so
    # every candidate dict has a consistent shape regardless of category.
    # ScoringEngine and all downstream tools never see raw DB rows — only
    # this dict.
    #
    # TODO: avg_meal_cost is a per-person recurring cost, not a one-time
    # entry fee. The budget scoring formula treats them the same for now
    # (approximate but acceptable). Revisit when the budget calculator
    # handles dining as a separate cost category.
    return {
        "id": str(row.id),
        "category": "restaurant",
        "name": row.name,
        "description": row.description,
        "rating": float(row.rating) if row.rating else 3.0,
        "entry_fee": float(row.avg_meal_cost) if row.avg_meal_cost else 0.0,
        "opening_hours": row.operating_hours,
        # Restaurants don't have a duration column. 60 minutes is a
        # reasonable default for a meal.
        # TODO: add duration_hours to restaurants if scheduling needs
        # refinement.
        "duration_minutes": _DEFAULT_RESTAURANT_DURATION_MINUTES,
        "latitude": float(row.latitude),
        "longitude": float(row.longitude),
        "starts_on": None,
        "ends_on": None,
        "event_start_time": None,
        "event_end_time": None,
        "similarity_score": None,
    }


def _serialize_hotel(row: Hotel) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "category": "hotel",
        "name": row.name,
        "description": row.description,
        "rating": float(row.rating) if row.rating else 3.0,
        # price_per_night used as the entry_fee equivalent for budget scoring.
        "entry_fee": float(row.price_per_night) if row.price_per_night else 0.0,
        # Hotels don't have opening hours — always available.
        "opening_hours": None,
        # Hotels are accommodation, not day activities. SchedulingEngine
        # handles hotels separately from attractions.
        "duration_minutes": None,
        "latitude": float(row.latitude),
        "longitude": float(row.longitude),
        "starts_on": None,
        "ends_on": None,
        "event_start_time": None,
        "event_end_time": None,
        "similarity_score": None,
    }


def _event_duration_minutes(schedule: dict[str, Any]) -> int:
    start_time = schedule.get("start_time")
    end_time = schedule.get("end_time")
    if not start_time or not end_time:
        return _DEFAULT_EVENT_DURATION_MINUTES

    start = time.fromisoformat(start_time)
    end = time.fromisoformat(end_time)
    start_minutes = start.hour * 60 + start.minute
    end_minutes = end.hour * 60 + end.minute
    return (end_minutes - start_minutes) % (24 * 60)


def _serialize_event(row: LocalEvent) -> dict[str, Any]:
    schedule = row.event_schedule or {}
    return {
        "id": str(row.id),
        "category": "local_event",
        "name": row.name,
        "description": row.description,
        "rating": float(row.rating) if row.rating else 3.0,
        "entry_fee": float(row.entry_fee) if row.entry_fee else 0.0,
        "opening_hours": row.opening_hours,
        # Duration derived from start_time/end_time in event_schedule JSONB.
        # Falls back to a default if either time is missing.
        "duration_minutes": _event_duration_minutes(schedule),
        "latitude": float(row.latitude),
        "longitude": float(row.longitude),
        # starts_on/ends_on are real DATE columns — queryable and indexable.
        # event_schedule JSONB now only carries time-of-day info (start_time,
        # end_time). Multi-day events (e.g. Kandy Esala Perahera) are
        # supported — admin sets starts_on and ends_on to different dates.
        "starts_on": row.starts_on.isoformat(),
        "ends_on": row.ends_on.isoformat(),
        "event_start_time": schedule.get("start_time"),
        "event_end_time": schedule.get("end_time"),
        "similarity_score": None,
    }


def retrieve_candidates(db: Session, destination: str | None) -> list[dict[str, Any]]:
    """Fetch attractions, restaurants, local events, and hotels for a destination.

    Filters by destination only. Interest/category matching is handled
    separately by the semantic matcher, not by this tool.
    """

    if not destination:
        return []

    matching_destination_ids = db.query(Destination.id).filter(
        Destination.name == destination
    )

    candidates: list[dict[str, Any]] = []

    for model, serialize in (
        (Attraction, _serialize_attraction),
        (Restaurant, _serialize_restaurant),
        (LocalEvent, _serialize_event),
        (Hotel, _serialize_hotel),
    ):
        rows = (
            db.query(model)
            .filter(
                model.destination_id.in_(matching_destination_ids),
                model.is_active.is_(True),
            )
            .all()
        )
        candidates.extend(serialize(row) for row in rows)

    return candidates


@tool
def candidate_retriever(destination: str | None = None) -> list[dict[str, Any]]:
    """Retrieve attractions, restaurants, local events, and hotels for a destination from the database."""

    db = SessionLocal()
    try:
        return retrieve_candidates(db, destination)
    finally:
        db.close()
