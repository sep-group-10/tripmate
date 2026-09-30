"""add planning session owner

Revision ID: c32a5170bf91
Revises: 9e9525136fc7
Create Date: 2026-09-30 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c32a5170bf91"
down_revision: str | Sequence[str] | None = "9e9525136fc7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add ownership and associate existing trip-backed sessions."""
    op.add_column(
        "planning_sessions",
        sa.Column("user_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_planning_sessions_user_id_users",
        "planning_sessions",
        "users",
        ["user_id"],
        ["id"],
    )
    op.execute(
        sa.text(
            "UPDATE planning_sessions AS planning_session "
            "SET user_id = trip.user_id "
            "FROM trips AS trip "
            "WHERE planning_session.trip_id = trip.id"
        )
    )


def downgrade() -> None:
    """Remove planning session ownership."""
    op.drop_constraint(
        "fk_planning_sessions_user_id_users",
        "planning_sessions",
        type_="foreignkey",
    )
    op.drop_column("planning_sessions", "user_id")
