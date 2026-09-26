"""add starts_on ends_on to local events

Revision ID: 9e9525136fc7
Revises: 2d29f259925e
Create Date: 2026-09-26 07:12:40.654321

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9e9525136fc7"
down_revision: str | Sequence[str] | None = "2d29f259925e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add queryable date-range columns for events, backfilled from the
    existing event_schedule JSONB. event_schedule keeps only time-of-day
    info (start_time, end_time) going forward."""
    op.add_column("local_events", sa.Column("starts_on", sa.Date(), nullable=True))
    op.add_column("local_events", sa.Column("ends_on", sa.Date(), nullable=True))

    op.execute(
        """
        UPDATE local_events
        SET starts_on = (event_schedule->>'date')::date,
            ends_on   = (event_schedule->>'date')::date
        WHERE event_schedule->>'date' IS NOT NULL
        """
    )

    op.alter_column("local_events", "starts_on", nullable=False)
    op.alter_column("local_events", "ends_on", nullable=False)

    op.create_index(
        "ix_local_events_date_range", "local_events", ["starts_on", "ends_on"]
    )


def downgrade() -> None:
    """Remove the date-range columns; event dates fall back to event_schedule."""
    op.drop_index("ix_local_events_date_range", table_name="local_events")
    op.drop_column("local_events", "ends_on")
    op.drop_column("local_events", "starts_on")
