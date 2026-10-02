"""allow trip drafts to omit unknown planning preferences

Revision ID: 3f7d2c91a6b4
Revises: b88335cc3898
Create Date: 2026-10-02
"""

import sqlalchemy as sa

from alembic import op

revision = "3f7d2c91a6b4"
down_revision = "b88335cc3898"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "trips", "travel_start_date", existing_type=sa.Date(), nullable=True
    )
    op.alter_column("trips", "travel_end_date", existing_type=sa.Date(), nullable=True)
    op.alter_column("trips", "duration", existing_type=sa.Integer(), nullable=True)
    op.alter_column(
        "trips",
        "budget",
        existing_type=sa.Numeric(precision=10, scale=2),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "trips",
        "budget",
        existing_type=sa.Numeric(precision=10, scale=2),
        nullable=False,
    )
    op.alter_column("trips", "duration", existing_type=sa.Integer(), nullable=False)
    op.alter_column("trips", "travel_end_date", existing_type=sa.Date(), nullable=False)
    op.alter_column(
        "trips", "travel_start_date", existing_type=sa.Date(), nullable=False
    )
