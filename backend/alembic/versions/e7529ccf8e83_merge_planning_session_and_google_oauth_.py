"""merge planning session and google oauth heads

Revision ID: e7529ccf8e83
Revises: 68ae3f7c0e8d, 6a2d088aa4db
Create Date: 2026-09-25 21:28:11.824911

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "e7529ccf8e83"
down_revision: str | Sequence[str] | None = ("68ae3f7c0e8d", "6a2d088aa4db")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
