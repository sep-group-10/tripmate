"""add starts_on ends_on to local events

Revision ID: 9e9525136fc7
Revises: 2d29f259925e
Create Date: 2026-09-26 07:12:40.654321

"""

from collections.abc import Sequence
from datetime import date

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
    connection = op.get_bind()
    invalid_count = 0
    invalid_ids: list[str] = []

    for row in connection.execute(
        sa.text("SELECT id, event_schedule->>'date' AS event_date FROM local_events")
    ):
        event_id, event_date = row
        try:
            parsed_date = (
                date.fromisoformat(event_date) if event_date is not None else None
            )
        except (TypeError, ValueError):
            parsed_date = None

        if parsed_date is None or parsed_date.isoformat() != event_date:
            invalid_count += 1
            if len(invalid_ids) < 10:
                invalid_ids.append(str(event_id))

    if invalid_count:
        sample = ", ".join(invalid_ids)
        remaining = invalid_count - len(invalid_ids)
        more = f" (and {remaining} more)" if remaining else ""
        raise RuntimeError(
            "Cannot add local event date columns: "
            f"{invalid_count} row(s) have a missing or invalid event_schedule.date. "
            f"Affected event IDs: {sample}{more}. "
            "Repair these values to ISO YYYY-MM-DD dates and rerun the migration."
        )

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
