"""update tourism models

Revision ID: 9aa643cd6d4e
Revises: 50eec33b9c88
Create Date: 2026-08-20 05:22:30.114250

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "9aa643cd6d4e"
down_revision: str | Sequence[str] | None = "50eec33b9c88"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    # ------------------------------------------------------------------
    # Attractions
    # ------------------------------------------------------------------

    op.add_column(
        "attractions",
        sa.Column(
            "latitude",
            sa.Numeric(precision=9, scale=6),
            nullable=True,
        ),
    )

    op.add_column(
        "attractions",
        sa.Column(
            "longitude",
            sa.Numeric(precision=9, scale=6),
            nullable=True,
        ),
    )

    op.add_column(
        "attractions",
        sa.Column(
            "photo_urls",
            postgresql.ARRAY(sa.Text()),
            nullable=True,
        ),
    )

    op.add_column(
        "attractions",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    # Existing attraction records inherit their destination coordinates
    # temporarily. These can later be replaced with actual attraction
    # coordinates.
    op.execute(
        """
        UPDATE attractions AS a
        SET
            latitude = (d.coordinates->>'latitude')::numeric,
            longitude = (d.coordinates->>'longitude')::numeric
        FROM destinations AS d
        WHERE a.destination_id = d.id
        """
    )

    op.alter_column(
        "attractions",
        "latitude",
        existing_type=sa.Numeric(precision=9, scale=6),
        nullable=False,
    )

    op.alter_column(
        "attractions",
        "longitude",
        existing_type=sa.Numeric(precision=9, scale=6),
        nullable=False,
    )

    op.alter_column(
        "attractions",
        "is_active",
        server_default=None,
    )

    op.drop_column("attractions", "category")

    # ------------------------------------------------------------------
    # Destinations
    # ------------------------------------------------------------------

    op.add_column(
        "destinations",
        sa.Column(
            "latitude",
            sa.Numeric(precision=9, scale=6),
            nullable=True,
        ),
    )

    op.add_column(
        "destinations",
        sa.Column(
            "longitude",
            sa.Numeric(precision=9, scale=6),
            nullable=True,
        ),
    )

    op.add_column(
        "destinations",
        sa.Column(
            "rating",
            sa.Numeric(precision=2, scale=1),
            nullable=True,
        ),
    )

    # Preserve existing destination coordinates.
    op.execute(
        """
        UPDATE destinations
        SET
            latitude = (coordinates->>'latitude')::numeric,
            longitude = (coordinates->>'longitude')::numeric
        WHERE coordinates IS NOT NULL
        """
    )

    op.alter_column(
        "destinations",
        "latitude",
        existing_type=sa.Numeric(precision=9, scale=6),
        nullable=False,
    )

    op.alter_column(
        "destinations",
        "longitude",
        existing_type=sa.Numeric(precision=9, scale=6),
        nullable=False,
    )

    op.drop_column("destinations", "coordinates")

    # ------------------------------------------------------------------
    # Hotels
    # ------------------------------------------------------------------

    op.add_column(
        "hotels",
        sa.Column(
            "latitude",
            sa.Numeric(precision=9, scale=6),
            nullable=True,
        ),
    )

    op.add_column(
        "hotels",
        sa.Column(
            "longitude",
            sa.Numeric(precision=9, scale=6),
            nullable=True,
        ),
    )

    # Existing hotel records inherit destination coordinates temporarily.
    op.execute(
        """
        UPDATE hotels AS h
        SET
            latitude = d.latitude,
            longitude = d.longitude
        FROM destinations AS d
        WHERE h.destination_id = d.id
        """
    )

    op.alter_column(
        "hotels",
        "latitude",
        existing_type=sa.Numeric(precision=9, scale=6),
        nullable=False,
    )

    op.alter_column(
        "hotels",
        "longitude",
        existing_type=sa.Numeric(precision=9, scale=6),
        nullable=False,
    )

    op.drop_column("hotels", "location")

    # ------------------------------------------------------------------
    # Local events
    # ------------------------------------------------------------------

    op.add_column(
        "local_events",
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "local_events",
        sa.Column(
            "latitude",
            sa.Numeric(precision=9, scale=6),
            nullable=True,
        ),
    )

    op.add_column(
        "local_events",
        sa.Column(
            "longitude",
            sa.Numeric(precision=9, scale=6),
            nullable=True,
        ),
    )

    op.add_column(
        "local_events",
        sa.Column(
            "photo_urls",
            postgresql.ARRAY(sa.Text()),
            nullable=True,
        ),
    )

    op.add_column(
        "local_events",
        sa.Column(
            "rating",
            sa.Numeric(precision=2, scale=1),
            nullable=True,
        ),
    )

    op.add_column(
        "local_events",
        sa.Column(
            "opening_hours",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )

    op.add_column(
        "local_events",
        sa.Column(
            "duration_hours",
            sa.Numeric(precision=4, scale=2),
            nullable=True,
        ),
    )

    op.add_column(
        "local_events",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    # Existing event records inherit destination coordinates temporarily.
    op.execute(
        """
        UPDATE local_events AS e
        SET
            latitude = d.latitude,
            longitude = d.longitude
        FROM destinations AS d
        WHERE e.destination_id = d.id
        """
    )

    op.alter_column(
        "local_events",
        "latitude",
        existing_type=sa.Numeric(precision=9, scale=6),
        nullable=False,
    )

    op.alter_column(
        "local_events",
        "longitude",
        existing_type=sa.Numeric(precision=9, scale=6),
        nullable=False,
    )

    op.alter_column(
        "local_events",
        "is_active",
        server_default=None,
    )

    op.drop_column("local_events", "category")

    # ------------------------------------------------------------------
    # Restaurants
    # ------------------------------------------------------------------

    op.add_column(
        "restaurants",
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "restaurants",
        sa.Column(
            "latitude",
            sa.Numeric(precision=9, scale=6),
            nullable=True,
        ),
    )

    op.add_column(
        "restaurants",
        sa.Column(
            "longitude",
            sa.Numeric(precision=9, scale=6),
            nullable=True,
        ),
    )

    op.add_column(
        "restaurants",
        sa.Column(
            "photo_urls",
            postgresql.ARRAY(sa.Text()),
            nullable=True,
        ),
    )

    op.add_column(
        "restaurants",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    # Existing restaurant records inherit destination coordinates temporarily.
    op.execute(
        """
        UPDATE restaurants AS r
        SET
            latitude = d.latitude,
            longitude = d.longitude
        FROM destinations AS d
        WHERE r.destination_id = d.id
        """
    )

    op.alter_column(
        "restaurants",
        "latitude",
        existing_type=sa.Numeric(precision=9, scale=6),
        nullable=False,
    )

    op.alter_column(
        "restaurants",
        "longitude",
        existing_type=sa.Numeric(precision=9, scale=6),
        nullable=False,
    )

    op.alter_column(
        "restaurants",
        "is_active",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    # ------------------------------------------------------------------
    # Restaurants
    # ------------------------------------------------------------------

    op.drop_column("restaurants", "is_active")
    op.drop_column("restaurants", "photo_urls")
    op.drop_column("restaurants", "longitude")
    op.drop_column("restaurants", "latitude")
    op.drop_column("restaurants", "description")

    # ------------------------------------------------------------------
    # Local events
    # ------------------------------------------------------------------

    op.add_column(
        "local_events",
        sa.Column(
            "category",
            sa.VARCHAR(length=100),
            nullable=False,
        ),
    )

    op.drop_column("local_events", "is_active")
    op.drop_column("local_events", "duration_hours")
    op.drop_column("local_events", "opening_hours")
    op.drop_column("local_events", "rating")
    op.drop_column("local_events", "photo_urls")
    op.drop_column("local_events", "longitude")
    op.drop_column("local_events", "latitude")
    op.drop_column("local_events", "description")

    # ------------------------------------------------------------------
    # Hotels
    # ------------------------------------------------------------------

    op.add_column(
        "hotels",
        sa.Column(
            "location",
            sa.VARCHAR(length=255),
            nullable=True,
        ),
    )

    op.drop_column("hotels", "longitude")
    op.drop_column("hotels", "latitude")

    # ------------------------------------------------------------------
    # Destinations
    # ------------------------------------------------------------------

    op.add_column(
        "destinations",
        sa.Column(
            "coordinates",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
        ),
    )

    # Reconstruct the old coordinates JSON from latitude/longitude.
    op.execute(
        """
        UPDATE destinations
        SET coordinates = json_build_object(
            'latitude', latitude,
            'longitude', longitude
        )
        """
    )

    op.drop_column("destinations", "rating")
    op.drop_column("destinations", "longitude")
    op.drop_column("destinations", "latitude")

    # ------------------------------------------------------------------
    # Attractions
    # ------------------------------------------------------------------

    op.add_column(
        "attractions",
        sa.Column(
            "category",
            sa.VARCHAR(length=100),
            nullable=False,
        ),
    )

    op.drop_column("attractions", "is_active")
    op.drop_column("attractions", "photo_urls")
    op.drop_column("attractions", "longitude")
    op.drop_column("attractions", "latitude")
