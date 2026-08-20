"""add tourism data constraints

Revision ID: a56691f36332
Revises: 9aa643cd6d4e
Create Date: 2026-08-20

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a56691f36332"
down_revision: Union[str, Sequence[str], None] = "9aa643cd6d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add database-level constraints for valid tourism data."""

    # Monetary values must not be negative.
    op.create_check_constraint(
        "ck_transport_rates_cost_per_km_non_negative",
        "transport_rates",
        "cost_per_km >= 0",
    )

    op.create_check_constraint(
        "ck_transport_rates_base_fare_non_negative",
        "transport_rates",
        "base_fare >= 0",
    )

    op.create_check_constraint(
        "ck_attractions_entry_fee_non_negative",
        "attractions",
        "entry_fee >= 0",
    )

    op.create_check_constraint(
        "ck_hotels_price_per_night_non_negative",
        "hotels",
        "price_per_night >= 0",
    )

    op.create_check_constraint(
        "ck_restaurants_avg_meal_cost_non_negative",
        "restaurants",
        "avg_meal_cost >= 0",
    )

    op.create_check_constraint(
        "ck_local_events_entry_fee_non_negative",
        "local_events",
        "entry_fee >= 0",
    )

    op.create_check_constraint(
        "ck_itinerary_day_items_estimated_cost_non_negative",
        "itinerary_day_items",
        "estimated_cost >= 0",
    )

    op.create_check_constraint(
        "ck_itineraries_total_estimated_cost_non_negative",
        "itineraries",
        "total_estimated_cost >= 0",
    )

    op.create_check_constraint(
        "ck_trips_budget_non_negative",
        "trips",
        "budget >= 0",
    )


def downgrade() -> None:
    """Remove database-level tourism data constraints."""

    op.drop_constraint(
        "ck_trips_budget_non_negative",
        "trips",
        type_="check",
    )

    op.drop_constraint(
        "ck_itineraries_total_estimated_cost_non_negative",
        "itineraries",
        type_="check",
    )

    op.drop_constraint(
        "ck_itinerary_day_items_estimated_cost_non_negative",
        "itinerary_day_items",
        type_="check",
    )

    op.drop_constraint(
        "ck_local_events_entry_fee_non_negative",
        "local_events",
        type_="check",
    )

    op.drop_constraint(
        "ck_restaurants_avg_meal_cost_non_negative",
        "restaurants",
        type_="check",
    )

    op.drop_constraint(
        "ck_hotels_price_per_night_non_negative",
        "hotels",
        type_="check",
    )

    op.drop_constraint(
        "ck_attractions_entry_fee_non_negative",
        "attractions",
        type_="check",
    )

    op.drop_constraint(
        "ck_transport_rates_base_fare_non_negative",
        "transport_rates",
        type_="check",
    )

    op.drop_constraint(
        "ck_transport_rates_cost_per_km_non_negative",
        "transport_rates",
        type_="check",
    )