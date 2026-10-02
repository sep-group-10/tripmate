"""add created_at and updated_at to trips

Revision ID: b21040fc20e2
Revises: dd3398cc90d3
Create Date: 2026-10-01
"""

import sqlalchemy as sa

from alembic import op

revision = "b21040fc20e2"
down_revision = "dd3398cc90d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "trips",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.add_column(
        "trips",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_column("trips", "updated_at")
    op.drop_column("trips", "created_at")
