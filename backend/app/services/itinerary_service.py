"""Persist generated chat itineraries using the existing itinerary tables."""

import uuid
from datetime import date, time
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy.orm import Session

from app.models.itinerary import Itinerary
from app.models.itinerary_day import ItineraryDay
from app.models.itinerary_day_item import ItineraryDayItem
from app.models.trip import Trip
from app.schemas.chat import ChatItinerary


def _estimated_cost(cost_estimate: dict[str, Any] | None) -> Decimal:
    """Return a representative estimate, or zero when no estimate exists."""
    total = cost_estimate.get("total") if isinstance(cost_estimate, dict) else None
    if not isinstance(total, dict):
        return Decimal("0.00")

    values: list[Decimal] = []
    for key in ("min", "max"):
        raw = total.get(key)
        if raw is None:
            continue
        try:
            amount = Decimal(str(raw))
        except (InvalidOperation, ValueError):
            continue
        if amount.is_finite() and amount >= 0:
            values.append(amount)

    if not values:
        return Decimal("0.00")
    if len(values) == 1:
        return values[0].quantize(Decimal("0.01"))
    return ((values[0] + values[1]) / 2).quantize(Decimal("0.01"))


def persist_chat_itinerary(
    db: Session,
    trip_id: uuid.UUID,
    itinerary: ChatItinerary,
    cost_estimate: dict[str, Any] | None = None,
) -> Itinerary:
    """Persist itinerary, days, and items atomically and mark its Trip generated.

    A connection-level savepoint protects this complete write set from partial
    saves without adding another ORM savepoint to the caller's Session. The
    caller remains responsible for committing its surrounding transaction.
    """
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise ValueError("Trip does not exist")

    # The test fixture (and some callers) already manages ORM savepoints. An
    # additional Session.begin_nested() triggers Session transaction-end
    # listeners when it closes, which can invalidate that surrounding
    # transaction. A savepoint on the bound connection keeps these writes
    # atomic without changing the Session transaction stack.
    with db.connection().begin_nested():
        record = Itinerary(
            trip_id=trip_id,
            total_estimated_cost=_estimated_cost(cost_estimate),
        )
        db.add(record)
        db.flush()

        for day in itinerary.days:
            day_record = ItineraryDay(
                itinerary_id=record.id,
                day_number=day.day_number,
                date=date.fromisoformat(day.date),
                title=day.day_type,
            )
            db.add(day_record)
            db.flush()

            for sort_order, item in enumerate(day.items):
                db.add(
                    ItineraryDayItem(
                        itinerary_day_id=day_record.id,
                        item_type=item.category,
                        title=item.name,
                        start_time=time.fromisoformat(item.start_time),
                        end_time=time.fromisoformat(item.end_time),
                        sort_order=sort_order,
                    )
                )

        trip.status = "generated"
        db.flush()

    return record


def persist_removed_chat_item(
    db: Session,
    trip_id: uuid.UUID,
    source_itinerary_id: uuid.UUID,
    target_item_id: uuid.UUID,
) -> Itinerary:
    """Persist a REMOVE revision while copying every unaffected stored field."""
    source = db.get(Itinerary, source_itinerary_id)
    trip = db.get(Trip, trip_id)
    if source is None or source.trip_id != trip_id or trip is None:
        raise ValueError("Current itinerary does not exist for this trip")
    latest = (
        db.query(Itinerary)
        .filter(Itinerary.trip_id == trip_id)
        .order_by(Itinerary.created_at.desc(), Itinerary.id.desc())
        .first()
    )
    if latest is None or latest.id != source_itinerary_id:
        raise ValueError("Current itinerary changed before the edit was saved")

    source_days = (
        db.query(ItineraryDay)
        .filter(ItineraryDay.itinerary_id == source.id)
        .order_by(ItineraryDay.day_number, ItineraryDay.id)
        .all()
    )
    with db.connection().begin_nested():
        revision = Itinerary(
            trip_id=trip_id,
            total_estimated_cost=source.total_estimated_cost,
            route_info=source.route_info,
            weather_info=source.weather_info,
        )
        db.add(revision)
        db.flush()
        found_target = False
        for source_day in source_days:
            day = ItineraryDay(
                itinerary_id=revision.id,
                day_number=source_day.day_number,
                date=source_day.date,
                title=source_day.title,
                summary=source_day.summary,
            )
            db.add(day)
            db.flush()
            source_items = (
                db.query(ItineraryDayItem)
                .filter(ItineraryDayItem.itinerary_day_id == source_day.id)
                .order_by(ItineraryDayItem.sort_order, ItineraryDayItem.id)
                .all()
            )
            next_order = 0
            for item in source_items:
                if item.id == target_item_id:
                    found_target = True
                    continue
                db.add(
                    ItineraryDayItem(
                        itinerary_day_id=day.id,
                        item_type=item.item_type,
                        title=item.title,
                        description=item.description,
                        start_time=item.start_time,
                        end_time=item.end_time,
                        location=item.location,
                        estimated_cost=item.estimated_cost,
                        sort_order=next_order,
                    )
                )
                next_order += 1
        if not found_target:
            raise ValueError("Target item is not in the current itinerary")
        trip.status = "generated"
        db.flush()
    return revision
