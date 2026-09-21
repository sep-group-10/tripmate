"""allow planning sessions without trips

Revision ID: 68ae3f7c0e8d
Revises: be0bf42d43c8
Create Date: 2026-09-19 03:39:15.705107

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "68ae3f7c0e8d"
down_revision: Union[str, Sequence[str], None] = "be0bf42d43c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Allow a planning session to exist before a trip is created."""
    op.alter_column(
        "planning_sessions",
        "trip_id",
        existing_type=sa.UUID(),
        nullable=True,
    )


def downgrade() -> None:
    """Require every planning session to have a trip again."""
    op.alter_column(
        "planning_sessions",
        "trip_id",
        existing_type=sa.UUID(),
        nullable=False,
    )
