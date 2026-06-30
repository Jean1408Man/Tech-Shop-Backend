"""Add pedidos

Revision ID: d3e4f5a6b7c8
Revises: c7d8e9f0a1b2
Create Date: 2026-06-29 04:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = "d3e4f5a6b7c8"
down_revision: Union[str, None] = "c7d8e9f0a1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pedidos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "fecha",
            mysql.TIMESTAMP(fsp=6),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("telefono", sa.String(length=30), nullable=False),
        sa.Column("total", sa.Numeric(10, 2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pedidos_id"), "pedidos", ["id"], unique=False)

    op.create_table(
        "pedido_productos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("producto_id", sa.Integer(), nullable=True),
        sa.Column("oferta_id", sa.Integer(), nullable=True),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("producto_nombre", sa.String(length=100), nullable=False),
        sa.Column("precio_unitario", sa.Numeric(10, 2), nullable=False),
        sa.Column("oferta_nombre", sa.String(length=100), nullable=True),
        sa.Column("descuento_unitario", sa.Numeric(10, 2), nullable=False),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        sa.ForeignKeyConstraint(["oferta_id"], ["ofertas.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["pedido_id"], ["pedidos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["producto_id"], ["productos.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pedido_productos_id"),
        "pedido_productos",
        ["id"],
        unique=False,
    )

    op.create_table(
        "pedido_combos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("combo_id", sa.Integer(), nullable=True),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("combo_nombre", sa.String(length=100), nullable=False),
        sa.Column("precio_unitario", sa.Numeric(10, 2), nullable=False),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        sa.ForeignKeyConstraint(["combo_id"], ["combos.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["pedido_id"], ["pedidos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pedido_combos_id"),
        "pedido_combos",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_pedido_combos_id"), table_name="pedido_combos")
    op.drop_table("pedido_combos")
    op.drop_index(op.f("ix_pedido_productos_id"), table_name="pedido_productos")
    op.drop_table("pedido_productos")
    op.drop_index(op.f("ix_pedidos_id"), table_name="pedidos")
    op.drop_table("pedidos")
