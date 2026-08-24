from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.transport_rate import TransportRate


def calculate_transport_cost(
    db: Session,
    transport_type: str,
    region: str,
    distance_km: Decimal,
) -> dict[str, Decimal]:
    """Calculate a transport cost range using the stored regional rate."""

    rate = (
        db.query(TransportRate)
        .filter(
            TransportRate.transport_type == transport_type,
            TransportRate.region == region,
        )
        .first()
    )

    if rate is None:
        raise ValueError(f"No transport rate found for {transport_type} in {region}")

    if distance_km < 0:
        raise ValueError("Distance cannot be negative")

    base_cost = rate.base_fare + (rate.cost_per_km * distance_km)

    minimum_cost = base_cost * Decimal("0.90")
    maximum_cost = base_cost * Decimal("1.10")

    return {
        "minimum_cost": minimum_cost.quantize(Decimal("0.01")),
        "maximum_cost": maximum_cost.quantize(Decimal("0.01")),
    }
