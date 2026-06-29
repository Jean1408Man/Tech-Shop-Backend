"""Add product, offer and combo tables

Revision ID: b4c3f9a1d2e7
Revises: 7a7964fa18b8
Create Date: 2026-06-29 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = "b4c3f9a1d2e7"
down_revision: Union[str, None] = "7a7964fa18b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "productos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("precio_base", sa.Numeric(10, 2), nullable=False),
        sa.Column("url_img", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_productos_id"), "productos", ["id"], unique=False)
    op.create_index(op.f("ix_productos_nombre"), "productos", ["nombre"], unique=False)

    op.create_table(
        "ofertas",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "fecha_creacion",
            mysql.TIMESTAMP(fsp=6),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.Column("fecha_inicio", sa.DateTime(), nullable=False),
        sa.Column("fecha_fin", sa.DateTime(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("monto_descuento", sa.Numeric(10, 2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ofertas_id"), "ofertas", ["id"], unique=False)
    op.create_index(op.f("ix_ofertas_nombre"), "ofertas", ["nombre"], unique=False)

    op.create_table(
        "combos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("precio", sa.Numeric(10, 2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_combos_id"), "combos", ["id"], unique=False)
    op.create_index(op.f("ix_combos_nombre"), "combos", ["nombre"], unique=False)

    op.create_table(
        "producto_oferta",
        sa.Column("producto_id", sa.Integer(), nullable=False),
        sa.Column("oferta_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["oferta_id"],
            ["ofertas.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["producto_id"],
            ["productos.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("producto_id", "oferta_id"),
    )

    op.create_table(
        "producto_combo",
        sa.Column("producto_id", sa.Integer(), nullable=False),
        sa.Column("combo_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["combo_id"],
            ["combos.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["producto_id"],
            ["productos.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("producto_id", "combo_id"),
    )


def downgrade() -> None:
    op.drop_table("producto_combo")
    op.drop_table("producto_oferta")
    op.drop_index(op.f("ix_combos_nombre"), table_name="combos")
    op.drop_index(op.f("ix_combos_id"), table_name="combos")
    op.drop_table("combos")
    op.drop_index(op.f("ix_ofertas_nombre"), table_name="ofertas")
    op.drop_index(op.f("ix_ofertas_id"), table_name="ofertas")
    op.drop_table("ofertas")
    op.drop_index(op.f("ix_productos_nombre"), table_name="productos")
    op.drop_index(op.f("ix_productos_id"), table_name="productos")
    op.drop_table("productos")
