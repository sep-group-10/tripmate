"""Transport rates by region. The cost estimator looks rates up by the
destination's ``region`` and needs all six types for a region to price a
local leg without warnings."""

from decimal import Decimal

# transport_type -> (cost_per_km, base_fare)
_RATES_BY_REGION = {
    "Western Province": {
        "bus_budget": ("0.30", "0.50"),
        "bus_luxury": ("0.50", "1.00"),
        "train": ("0.20", "1.00"),
        "tuk_tuk": ("1.00", "1.50"),
        "car": ("1.50", "2.00"),
        "van": ("1.80", "2.50"),
    },
    "Central Province": {
        "bus_budget": ("0.35", "0.50"),
        "bus_luxury": ("0.55", "1.00"),
        "train": ("0.22", "1.00"),
        "tuk_tuk": ("1.10", "1.50"),
        "car": ("1.60", "2.00"),
        "van": ("1.90", "2.50"),
    },
    "Southern Province": {
        "bus_budget": ("0.32", "0.50"),
        "bus_luxury": ("0.52", "1.00"),
        "train": ("0.21", "1.00"),
        "tuk_tuk": ("1.05", "1.50"),
        "car": ("1.55", "2.00"),
        "van": ("1.85", "2.50"),
    },
    "North Central Province": {
        "bus_budget": ("0.34", "0.50"),
        "bus_luxury": ("0.54", "1.00"),
        "train": ("0.22", "1.00"),
        "tuk_tuk": ("1.10", "1.50"),
        "car": ("1.60", "2.00"),
        "van": ("1.90", "2.50"),
    },
    "Eastern Province": {
        "bus_budget": ("0.36", "0.50"),
        "bus_luxury": ("0.56", "1.00"),
        "train": ("0.22", "1.00"),
        "tuk_tuk": ("1.15", "1.50"),
        "car": ("1.65", "2.00"),
        "van": ("1.95", "2.50"),
    },
    "Uva Province": {
        "bus_budget": ("0.36", "0.50"),
        "bus_luxury": ("0.56", "1.00"),
        "train": ("0.23", "1.00"),
        "tuk_tuk": ("1.15", "1.50"),
        "car": ("1.65", "2.00"),
        "van": ("1.95", "2.50"),
    },
}

TRANSPORT_RATES = [
    {
        "transport_type": transport_type,
        "region": region,
        "cost_per_km": Decimal(cost_per_km),
        "base_fare": Decimal(base_fare),
    }
    for region, rates in _RATES_BY_REGION.items()
    for transport_type, (cost_per_km, base_fare) in rates.items()
]
