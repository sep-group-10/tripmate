"""add embedding columns to tourism tables

Revision ID: 2a8a6b0e5945
Revises: e7529ccf8e83
Create Date: 2026-09-26 06:11:28.453076

"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op
from app.core.embedding import EMBEDDING_DIMENSION

# revision identifiers, used by Alembic.
revision: str = "2a8a6b0e5945"
down_revision: str | Sequence[str] | None = "e7529ccf8e83"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLES = ("attractions", "hotels", "restaurants", "local_events")


def upgrade() -> None:
    """Add embedding columns needed for the future SemanticMatcher tool."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    for table in _TABLES:
        op.add_column(
            table,
            sa.Column(
                "description_embedding",
                Vector(EMBEDDING_DIMENSION),
                nullable=True,
            ),
        )
        op.add_column(
            table,
            sa.Column(
                "embedding_status",
                sa.String(),
                nullable=False,
                server_default="pending",
            ),
        )
        op.create_check_constraint(
            f"ck_{table}_embedding_status_valid",
            table,
            "embedding_status IN ('pending', 'ready', 'failed')",
        )


def downgrade() -> None:
    """Remove embedding columns."""
    for table in _TABLES:
        op.drop_constraint(f"ck_{table}_embedding_status_valid", table, type_="check")
        op.drop_column(table, "embedding_status")
        op.drop_column(table, "description_embedding")
