"""Merge feedback-fields and itinerary-revision heads.

Revision ID: cb3efb69455a
Revises: 056eddbfd92f, f18a3c7d9b42
Create Date: 2026-10-03
"""

from collections.abc import Sequence

revision: str = "cb3efb69455a"
down_revision: str | Sequence[str] | None = ("056eddbfd92f", "f18a3c7d9b42")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
