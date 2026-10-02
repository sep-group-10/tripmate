"""Add feedback resolution fields.

Revision ID: 056eddbfd92f
Revises: f18a2b6c9d40
Create Date: 2026-10-02
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "056eddbfd92f"
down_revision: str | Sequence[str] | None = "f18a2b6c9d40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "feedback",
        sa.Column("resolution_outcome", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "feedback",
        sa.Column("resolution_note", sa.Text(), nullable=True),
    )
    op.add_column(
        "feedback",
        sa.Column("resolved_by", sa.UUID(), nullable=True),
    )
    op.add_column(
        "feedback",
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_foreign_key(
        "feedback_resolved_by_fkey", "feedback", "users", ["resolved_by"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("feedback_resolved_by_fkey", "feedback", type_="foreignkey")
    op.drop_column("feedback", "resolved_at")
    op.drop_column("feedback", "resolved_by")
    op.drop_column("feedback", "resolution_note")
    op.drop_column("feedback", "resolution_outcome")
