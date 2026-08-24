"""add region to transport rates

Revision ID: be0bf42d43c8
Revises: a56691f36332
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "be0bf42d43c8"
down_revision: str | Sequence[str] | None = "a56691f36332"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "transport_rates",
        sa.Column(
            "region",
            sa.String(length=100),
            nullable=True,
        ),
    )

    # Give existing transport rates a temporary region.
    op.execute(
        """
        UPDATE transport_rates
        SET region = 'General'
        WHERE region IS NULL
        """
    )

    op.alter_column(
        "transport_rates",
        "region",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    op.create_unique_constraint(
        "uq_transport_rates_type_region",
        "transport_rates",
        ["transport_type", "region"],
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE transport_rates
        DROP CONSTRAINT IF EXISTS uq_transport_rates_type_region
        """
    )

    op.drop_column(
        "transport_rates",
        "region",
    )
