"""Add images to offers and combos

Revision ID: a5f4c8d9e1b2
Revises: b4c3f9a1d2e7
Create Date: 2026-06-29 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a5f4c8d9e1b2"
down_revision: Union[str, None] = "b4c3f9a1d2e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ofertas", sa.Column("imagen", sa.String(length=500), nullable=True))
    op.add_column("combos", sa.Column("imagen", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("combos", "imagen")
    op.drop_column("ofertas", "imagen")
