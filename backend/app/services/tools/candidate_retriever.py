"""Candidate retrieval tool for the TripMate planning graph."""

from typing import Any

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.attraction import Attraction
from app.models.destination import Destination
from app.models.hotel import Hotel
from app.models.local_event import LocalEvent
from app.models.restaurant import Restaurant


def _serialize(
    row: Attraction | Restaurant | LocalEvent | Hotel, category: str
) -> dict[str, Any]:
    base = {
        "id": str(row.id),
        "category": category,
        "name": row.name,
        "description": row.description,
        "rating": row.rating,
    }

    if isinstance(row, Restaurant):
        # avg_meal_cost and operating_hours are the correct DB column names for
        # restaurants. They are normalized here to entry_fee and opening_hours so
        # every candidate dict has a consistent shape regardless of entity type.
        # ScoringEngine and all downstream tools never see raw DB rows — only this
        # dict.
        #
        # TODO: avg_meal_cost is a per-person recurring cost, not a one-time entry
        # fee. The budget scoring formula treats them the same for now (approximate
        # but acceptable). Revisit when the budget calculator handles dining as a
        # separate cost category.
        base["entry_fee"] = row.avg_meal_cost
        base["opening_hours"] = row.operating_hours
    elif isinstance(row, Attraction | LocalEvent):
        base["entry_fee"] = row.entry_fee
        base["opening_hours"] = row.opening_hours

    return base


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

    for model, category in (
        (Attraction, "attraction"),
        (Restaurant, "restaurant"),
        (LocalEvent, "local_event"),
        (Hotel, "hotel"),
    ):
        rows = (
            db.query(model)
            .filter(
                model.destination_id.in_(matching_destination_ids),
                model.is_active.is_(True),
            )
            .all()
        )
        candidates.extend(_serialize(row, category) for row in rows)

    return candidates


@tool
def candidate_retriever(destination: str | None = None) -> list[dict[str, Any]]:
    """Retrieve attractions, restaurants, local events, and hotels for a destination from the database."""

    db = SessionLocal()
    try:
        return retrieve_candidates(db, destination)
    finally:
        db.close()
