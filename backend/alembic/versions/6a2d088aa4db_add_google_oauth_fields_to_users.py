"""add google oauth fields to users

Revision ID: 6a2d088aa4db
Revises: be0bf42d43c8
Create Date: 2026-09-18 23:46:00.970394

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "6a2d088aa4db"
down_revision: str | Sequence[str] | None = "be0bf42d43c8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Google-only accounts have no password at all.
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(length=255),
        nullable=True,
    )

    op.add_column(
        "users",
        sa.Column(
            "login_provider",
            sa.String(length=20),
            nullable=False,
            server_default="local",
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "google_id",
            sa.String(length=255),
            nullable=True,
        ),
    )
    op.create_unique_constraint(
        "uq_users_google_id",
        "users",
        ["google_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_users_google_id", "users", type_="unique")
    op.drop_column("users", "google_id")
    op.drop_column("users", "login_provider")

    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(length=255),
        nullable=False,
    )
