"""add profile picture url to users

Revision ID: dd3398cc90d3
Revises: b31c4af8e902
Create Date: 2026-10-01
"""

import sqlalchemy as sa

from alembic import op

revision = "dd3398cc90d3"
down_revision = "b31c4af8e902"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("profile_picture_url", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "profile_picture_url")
