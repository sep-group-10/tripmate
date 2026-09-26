from decimal import Decimal

import pytest

from app.services import routing


@pytest.fixture(autouse=True)
def _clear_routing_cache():
    routing.clear_cache()
    yield
    routing.clear_cache()


def test_estimate_travel_time_same_point_is_zero():
    estimate = routing.estimate_travel_time(
        Decimal("7.2906"), Decimal("80.6337"), Decimal("7.2906"), Decimal("80.6337")
    )

    assert estimate.distance_km == 0.0
    assert estimate.duration_minutes == 0
    assert estimate.travel_source == "estimate"


def test_estimate_travel_time_increases_with_distance():
    kandy_to_colombo = routing.estimate_travel_time(
        Decimal("7.2906"), Decimal("80.6337"), Decimal("6.9271"), Decimal("79.8612")
    )
    kandy_to_kandy_lake = routing.estimate_travel_time(
        Decimal("7.2906"), Decimal("80.6337"), Decimal("7.2915"), Decimal("80.6350")
    )

    assert kandy_to_colombo.duration_minutes > kandy_to_kandy_lake.duration_minutes


def test_estimate_travel_time_rounds_to_nearest_15_minutes():
    estimate = routing.estimate_travel_time(
        Decimal("7.2906"), Decimal("80.6337"), Decimal("6.9271"), Decimal("79.8612")
    )

    assert estimate.duration_minutes % 15 == 0


def test_estimate_travel_time_always_tagged_estimate():
    estimate = routing.estimate_travel_time(
        Decimal("7.2906"), Decimal("80.6337"), Decimal("6.9271"), Decimal("79.8612")
    )

    assert estimate.travel_source == "estimate"


def test_estimate_travel_time_is_cached():
    first = routing.estimate_travel_time(
        Decimal("7.2906"), Decimal("80.6337"), Decimal("6.9271"), Decimal("79.8612")
    )
    second = routing.estimate_travel_time(
        Decimal("7.2906"), Decimal("80.6337"), Decimal("6.9271"), Decimal("79.8612")
    )

    assert first is second


def test_estimate_travel_time_accepts_plain_floats():
    estimate = routing.estimate_travel_time(7.2906, 80.6337, 6.9271, 79.8612)

    assert estimate.duration_minutes > 0
