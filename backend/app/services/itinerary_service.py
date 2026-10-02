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
