"""Add photo URLs to destinations.

Revision ID: f18a2b6c9d40
Revises: d4a3e81b2c90
Create Date: 2026-10-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "f18a2b6c9d40"
down_revision: str | Sequence[str] | None = "d4a3e81b2c90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "destinations",
        sa.Column("photo_urls", postgresql.ARRAY(postgresql.TEXT()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("destinations", "photo_urls")
