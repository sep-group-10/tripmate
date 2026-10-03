"""add created_at to itineraries

Revision ID: 4e6d7b2a91c3
Revises: d4a3e81b2c90
Create Date: 2026-10-02

Existing itinerary rows receive the migration transaction timestamp. That
provides a safe non-null backfill without deleting or distinguishing historical
rows whose generation order is not recorded. The retrieval query uses the ID
only as a deterministic tie-breaker for rows with equal timestamps; it does not
represent or reconstruct their historical generation order.
"""

import sqlalchemy as sa

from alembic import op

revision = "4e6d7b2a91c3"
down_revision = "d4a3e81b2c90"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "itineraries",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_column("itineraries", "created_at")
