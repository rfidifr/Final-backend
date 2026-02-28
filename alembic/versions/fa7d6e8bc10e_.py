"""empty message

Revision ID: fa7d6e8bc10e
Revises: b3c99c20cc86
Create Date: 2026-02-25 12:58:26.768743

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa7d6e8bc10e'
down_revision: Union[str, Sequence[str], None] = 'b3c99c20cc86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
