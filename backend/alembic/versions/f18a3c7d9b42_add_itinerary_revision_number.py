"""add nullable itinerary revision ordering

Revision ID: f18a3c7d9b42
Revises: 4e6d7b2a91c3
Create Date: 2026-10-03

Legacy rows remain NULL because their historical ordering cannot be recovered.
"""

import sqlalchemy as sa

from alembic import op

revision = "f18a3c7d9b42"
down_revision = "4e6d7b2a91c3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "itineraries",
        sa.Column("revision_number", sa.Integer(), nullable=True),
    )
    op.create_unique_constraint(
        "uq_itineraries_trip_revision_number",
        "itineraries",
        ["trip_id", "revision_number"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_itineraries_trip_revision_number",
        "itineraries",
        type_="unique",
    )
    op.drop_column("itineraries", "revision_number")
