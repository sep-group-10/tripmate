"""add preferred pace to users

Revision ID: b31c4af8e902
Revises: c32a5170bf91
Create Date: 2026-10-01
"""

import sqlalchemy as sa

from alembic import op

revision = "b31c4af8e902"
down_revision = "c32a5170bf91"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("preferred_pace", sa.String(length=100), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "preferred_pace")
