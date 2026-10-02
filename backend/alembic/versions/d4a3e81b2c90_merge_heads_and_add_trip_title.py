"""merge draft migration head and add optional trip title

Revision ID: d4a3e81b2c90
Revises: 3f7d2c91a6b4, e7529ccf8e83
Create Date: 2026-10-02
"""

import sqlalchemy as sa

from alembic import op

revision = "d4a3e81b2c90"
down_revision = ("3f7d2c91a6b4", "e7529ccf8e83")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("trips", sa.Column("title", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("trips", "title")
