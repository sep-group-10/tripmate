from decimal import Decimal

import pytest

from app.services.transport_cost import calculate_transport_cost


def test_calculate_transport_cost_uses_regional_rate(db_session):
    result = calculate_transport_cost(
        db=db_session,
        transport_type="car",
        region="Western Province",
        distance_km=Decimal(100),
    )

    assert result["minimum_cost"] == Decimal("136.80")
    assert result["maximum_cost"] == Decimal("167.20")


def test_calculate_transport_cost_returns_range(db_session):
    result = calculate_transport_cost(
        db=db_session,
        transport_type="train",
        region="Central Province",
        distance_km=Decimal(100),
    )

    assert result["minimum_cost"] < result["maximum_cost"]
    assert result["minimum_cost"] == Decimal("20.70")
    assert result["maximum_cost"] == Decimal("25.30")


def test_calculate_transport_cost_rejects_negative_distance(db_session):
    with pytest.raises(ValueError, match="Distance cannot be negative"):
        calculate_transport_cost(
            db=db_session,
            transport_type="car",
            region="Western Province",
            distance_km=Decimal(-10),
        )


def test_calculate_transport_cost_requires_matching_region(db_session):
    with pytest.raises(
        ValueError,
        match="No transport rate found",
    ):
        calculate_transport_cost(
            db=db_session,
            transport_type="car",
            region="Unknown Province",
            distance_km=Decimal(100),
        )
