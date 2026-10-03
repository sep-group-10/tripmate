"""Seed data for the tourism tables, one module per destination.

To add a destination, drop a new module in this package that defines a
``DESTINATION`` dict -- it is discovered automatically, no seed logic needs
editing. If the destination's ``region`` has no rates yet, add them to
``transport_rates.py`` (the cost estimator prices local travel by region).

``DESTINATION`` shape (see kandy.py for a full example)::

    {
        "name", "description", "country", "region", "latitude", "longitude",
        "is_active",
        "id": optional fixed UUID, used only when the row is first inserted,
        "planner_ready": False if the destination is knowingly incomplete
            (no hotels etc.); tests skip the completeness checks for it,
        "attractions": [{name, description, latitude, longitude, entry_fee,
                         duration_hours, rating, opening_hours}],
        "hotels": [{name, description, latitude, longitude, price_per_night,
                    facilities, rating}],
        "restaurants": [{name, description, latitude, longitude, cuisine_type,
                         avg_meal_cost, rating, operating_hours}],
        "events": [{name, description, latitude, longitude, entry_fee, rating,
                    days_ahead, duration_days, start_time, end_time}],
        "deactivate_attractions": names (case-insensitive) of stale rows to
            set is_active=false; rows are never deleted,
    }

Events carry ``days_ahead`` rather than dates: the seed turns it into
``starts_on``/``ends_on`` relative to the day it runs, so a re-run always
yields future events.
"""

import importlib
import pkgutil

from app.core.seed_data.transport_rates import TRANSPORT_RATES


def _load_destinations() -> list[dict]:
    found = []
    for module_info in pkgutil.iter_modules(__path__):
        if module_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{__name__}.{module_info.name}")
        destination = getattr(module, "DESTINATION", None)
        if destination is not None:
            found.append(destination)
    return sorted(found, key=lambda destination: destination["name"])


DESTINATION_SEEDS = _load_destinations()

__all__ = ["DESTINATION_SEEDS", "TRANSPORT_RATES"]
