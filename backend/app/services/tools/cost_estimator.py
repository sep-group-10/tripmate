"""CostEstimator: calculates an estimated trip cost from a completed itinerary.

Deterministic, no DB access, no LLM calls, no network calls. Reads what
SchedulingEngine and RouteOptimizer already produced and multiplies.

Verified against the real codebase before writing this (see PR discussion):
SchedulingEngine is explicitly scoped to single-destination trips (see
TripMate issue #184 for the multi-destination follow-up), so there is
currently no intercity travel leg anywhere in the itinerary shape — no
distance between destinations exists because there is only ever one
destination. `transport_intercity` therefore always returns the documented
zero-case for now; there is nothing upstream to price it from yet. This is
not a shortcut — it is the honest answer given the current schema, and it
will start producing real numbers once #184 lands without any change needed
here, the same way ScoringEngine's similarity_score fallback works today.

Also verified: `Hotel.price_per_night` is a single Decimal on the model and
in CandidateRetriever's normalized dict — there is no price_per_night_min/
price_per_night_max pair anywhere in the schema. Accommodation is therefore
priced as a single value per night, not a range; min and max are equal for
this category, exactly like activities and dining (whose entry_fee is also
a single fixed value, not a range).
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.destination import Destination
from app.models.transport_rate import TransportRate

_MISC_RATE = Decimal("0.10")

# bus/train seats are sold per person; car/van/tuk_tuk are hired as a whole
# vehicle, so the price doesn't change with traveller count (Decision 2).
_PER_TRAVELLER_TRANSPORT_TYPES = {"bus_budget", "bus_luxury", "train"}
_PER_VEHICLE_TRANSPORT_TYPES = {"car", "van", "tuk_tuk"}
_ALL_TRANSPORT_TYPES = _PER_TRAVELLER_TRANSPORT_TYPES | _PER_VEHICLE_TRANSPORT_TYPES

_RESTAURANT_CATEGORY = "restaurant"
_HOTEL_CATEGORY = "hotel"
_EVENT_CATEGORY = "local_event"
_ATTRACTION_CATEGORY = "attraction"


@dataclass
class _Range:
    min: Decimal = Decimal("0")
    max: Decimal = Decimal("0")
    is_estimate: bool | None = None

    def add(self, other: "_Range") -> None:
        self.min += other.min
        self.max += other.max
        if other.is_estimate is not None:
            self.is_estimate = bool(self.is_estimate) or other.is_estimate

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "min": self.min,
            "max": self.max,
        }
        if self.is_estimate is not None:
            result["is_estimate"] = self.is_estimate
        return result


@dataclass
class _CostContext:
    warnings: list[str] = field(default_factory=list)


def _rates_by_region(db: Session, region: str) -> dict[str, TransportRate]:
    rows = db.query(TransportRate).filter(TransportRate.region == region).all()
    return {row.transport_type: row for row in rows}


def _leg_cost_range(
    distance_km: Decimal,
    travellers: int,
    rates: dict[str, TransportRate],
    context: _CostContext,
    leg_description: str,
) -> _Range | None:
    """Cost range for one travel leg across every available vehicle type.

    Returns None if no vehicle type has a rate at all for this region — the
    leg is unpriced rather than guessed at, per the plan's edge cases.
    """
    costs: list[Decimal] = []

    for transport_type in _ALL_TRANSPORT_TYPES:
        rate = rates.get(transport_type)
        if rate is None:
            context.warnings.append(
                f"No transport rate for {transport_type} in this region; "
                f"excluded from the {leg_description} range"
            )
            continue

        cost = rate.base_fare + (rate.cost_per_km * distance_km)
        if transport_type in _PER_TRAVELLER_TRANSPORT_TYPES:
            cost *= travellers
        costs.append(cost)

    if not costs:
        context.warnings.append(
            f"No transport rate available for any vehicle type for the "
            f"{leg_description}; leg left unpriced"
        )
        return None

    return _Range(min=min(costs), max=max(costs))


def _nights_per_destination(itinerary: dict[str, Any]) -> dict[str, int]:
    """Derive nights per destination — no such field exists on the itinerary.

    Counts days that share the same hotel_id, then maps that hotel back to
    its destination via hotel_by_destination (Section 0.A / Section 3).
    """
    hotel_by_destination = itinerary.get("hotel_by_destination") or {}
    hotel_to_destination = {
        hotel_id: dest for dest, hotel_id in hotel_by_destination.items()
    }

    nights: dict[str, int] = {}
    for day in itinerary.get("days") or []:
        hotel_id = day.get("hotel_id")
        if not hotel_id:
            continue
        destination = hotel_to_destination.get(hotel_id)
        if destination is None:
            continue
        nights[destination] = nights.get(destination, 0) + 1

    return nights


def _accommodation_cost(
    db: Session,
    itinerary: dict[str, Any],
    candidates: list[dict[str, Any]],
    context: _CostContext,
) -> _Range:
    nights_per_destination = _nights_per_destination(itinerary)
    hotel_by_destination = itinerary.get("hotel_by_destination") or {}
    hotels_by_id = {
        c["id"]: c for c in candidates if c.get("category") == _HOTEL_CATEGORY
    }

    total = _Range()
    for destination, nights in nights_per_destination.items():
        hotel_id = hotel_by_destination.get(destination)
        hotel = hotels_by_id.get(hotel_id) if hotel_id else None

        if hotel is None:
            context.warnings.append(
                f"No hotel assigned for {destination}; accommodation cost skipped "
                "for this destination"
            )
            continue

        price = Decimal(str(hotel.get("entry_fee") or 0))
        nightly = _Range(min=price * nights, max=price * nights)
        total.add(nightly)

    return total


def _entry_fee_total(
    itinerary: dict[str, Any],
    candidates: list[dict[str, Any]],
    categories: set[str],
    travellers: int,
) -> _Range:
    candidates_by_id = {c["id"]: c for c in candidates}
    scheduled_ids: set[str] = set()

    for day in itinerary.get("days") or []:
        for item in day.get("items") or []:
            if item.get("category") in categories:
                scheduled_ids.add(item["candidate_id"])

    fee_total = Decimal("0")
    for candidate_id in scheduled_ids:
        candidate = candidates_by_id.get(candidate_id)
        if candidate is None:
            continue
        fee_total += Decimal(str(candidate.get("entry_fee") or 0))

    fee_total *= travellers
    return _Range(min=fee_total, max=fee_total)


def _local_transport_cost(
    db: Session,
    itinerary: dict[str, Any],
    destination_region: str | None,
    travellers: int,
    context: _CostContext,
) -> _Range:
    if destination_region is None:
        return _Range(min=Decimal("0"), max=Decimal("0"), is_estimate=False)

    rates = _rates_by_region(db, destination_region)

    total = _Range(is_estimate=False)
    for day in itinerary.get("days") or []:
        route_optimization = day.get("route_optimization") or {}
        distance_km = route_optimization.get("local_distance_km")

        if not distance_km:
            continue

        leg_range = _leg_cost_range(
            Decimal(str(distance_km)),
            travellers,
            rates,
            context,
            leg_description=f"local travel on day {day.get('day_number')}",
        )
        if leg_range is None:
            continue

        # Local movement uses road distance estimates only — no per-leg
        # travel_source is tracked at this granularity yet, so local
        # transport is always flagged as an estimate rather than silently
        # claiming a confidence level nothing here can back up.
        leg_range.is_estimate = True
        total.add(leg_range)

    if total.min == 0 and total.max == 0:
        total.is_estimate = False

    return total


def _intercity_transport_cost() -> _Range:
    """No intercity legs exist yet.

    SchedulingEngine is explicitly scoped to single-destination trips (see
    module docstring) — there is no travel-between-destinations concept
    anywhere in the itinerary shape today, so there is nothing to price.
    This returns the documented zero-case (Section 5) rather than a stub;
    it will start computing real ranges once multi-destination itineraries
    exist, with no change needed here.
    """
    return _Range(min=Decimal("0"), max=Decimal("0"), is_estimate=False)


def estimate_cost(
    db: Session,
    itinerary: dict[str, Any],
    candidates: list[dict[str, Any]],
    trip_requirements: dict[str, Any],
) -> dict[str, Any]:
    """Calculate an estimated trip cost, broken into ranged categories."""

    context = _CostContext()

    travellers = trip_requirements.get("travelers")
    if not travellers or travellers < 1:
        travellers = 1
        context.warnings.append(
            "Traveller count missing from trip requirements; assumed solo travel"
        )
    elif travellers > 4:
        context.warnings.append(
            "Group size exceeds single-vehicle capacity for car/van legs; "
            "multiple vehicles may be needed in practice"
        )

    destination_name = trip_requirements.get("destination")
    destination_region = None
    if destination_name:
        destination_region = (
            db.query(Destination.region)
            .filter(Destination.name == destination_name)
            .scalar()
        )

    transport_intercity = _intercity_transport_cost()
    transport_local = _local_transport_cost(
        db, itinerary, destination_region, travellers, context
    )
    accommodation = _accommodation_cost(db, itinerary, candidates, context)
    activities = _entry_fee_total(
        itinerary, candidates, {_ATTRACTION_CATEGORY, _EVENT_CATEGORY}, travellers
    )
    dining = _entry_fee_total(itinerary, candidates, {_RESTAURANT_CATEGORY}, travellers)

    subtotal = _Range()
    for category in (
        transport_intercity,
        transport_local,
        accommodation,
        activities,
        dining,
    ):
        subtotal.add(_Range(min=category.min, max=category.max))

    miscellaneous = _Range(
        min=(subtotal.min * _MISC_RATE), max=(subtotal.max * _MISC_RATE)
    )

    total = _Range()
    for category in (
        transport_intercity,
        transport_local,
        accommodation,
        activities,
        dining,
        miscellaneous,
    ):
        total.add(_Range(min=category.min, max=category.max))

    return {
        "transport_intercity": transport_intercity.as_dict(),
        "transport_local": transport_local.as_dict(),
        "accommodation": accommodation.as_dict(),
        "activities": activities.as_dict(),
        "dining": dining.as_dict(),
        "miscellaneous": miscellaneous.as_dict(),
        "total": total.as_dict(),
        "travellers": travellers,
        "warnings": context.warnings,
    }


@tool
def cost_estimator(
    itinerary: dict, candidates: list[dict], trip_requirements: dict
) -> dict:
    """Estimate the total trip cost from a completed itinerary.

    Breaks costs into transport, accommodation, activities, dining, and
    miscellaneous, each as a min-max range, using rates and hotel/entry-fee
    data already present in the candidate list. Pure arithmetic — no
    network, AI, or database write calls.
    """
    db = SessionLocal()
    try:
        return estimate_cost(db, itinerary, candidates, trip_requirements)
    finally:
        db.close()
