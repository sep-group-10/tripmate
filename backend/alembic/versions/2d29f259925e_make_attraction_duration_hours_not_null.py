"""make attraction duration_hours not null

Revision ID: 2d29f259925e
Revises: 2a8a6b0e5945
Create Date: 2026-09-26 07:05:12.123456

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2d29f259925e"
down_revision: str | Sequence[str] | None = "2a8a6b0e5945"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Require a duration for every attraction so SchedulingEngine never
    has to guess how long a visit takes."""
    op.execute(
        "UPDATE attractions SET duration_hours = 1.0 WHERE duration_hours IS NULL"
    )

    op.alter_column(
        "attractions",
        "duration_hours",
        existing_type=sa.Numeric(4, 2),
        nullable=False,
        server_default="1.0",
    )


def downgrade() -> None:
    """Allow attractions without a recorded duration again."""
    op.alter_column(
        "attractions",
        "duration_hours",
        existing_type=sa.Numeric(4, 2),
        nullable=True,
        server_default=None,
    )
