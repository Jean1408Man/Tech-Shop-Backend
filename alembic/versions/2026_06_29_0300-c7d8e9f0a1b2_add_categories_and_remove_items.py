"""Add categories and remove items

Revision ID: c7d8e9f0a1b2
Revises: a5f4c8d9e1b2
Create Date: 2026-06-29 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c7d8e9f0a1b2"
down_revision: Union[str, None] = "a5f4c8d9e1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("url_img", sa.String(length=500), nullable=True),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_categorias_id"), "categorias", ["id"], unique=False)
    op.create_index(
        op.f("ix_categorias_nombre"),
        "categorias",
        ["nombre"],
        unique=False,
    )

    op.add_column("productos", sa.Column("categoria_id", sa.Integer(), nullable=True))

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            INSERT INTO categorias (nombre, url_img, descripcion)
            VALUES (:nombre, NULL, :descripcion)
            """
        ),
        {
            "nombre": "Sin categoria",
            "descripcion": "Categoria asignada a productos existentes.",
        },
    )
    default_categoria_id = connection.execute(
        sa.text(
            """
            SELECT id
            FROM categorias
            WHERE nombre = :nombre
            ORDER BY id DESC
            LIMIT 1
            """
        ),
        {"nombre": "Sin categoria"},
    ).scalar_one()
    connection.execute(
        sa.text(
            """
            UPDATE productos
            SET categoria_id = :categoria_id
            WHERE categoria_id IS NULL
            """
        ),
        {"categoria_id": default_categoria_id},
    )

    op.alter_column(
        "productos",
        "categoria_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_foreign_key(
        "fk_productos_categoria_id_categorias",
        "productos",
        "categorias",
        ["categoria_id"],
        ["id"],
    )

    inspector = sa.inspect(connection)
    if "items" in inspector.get_table_names():
        op.drop_table("items")


def downgrade() -> None:
    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_items_id"), "items", ["id"], unique=False)
    op.create_index(op.f("ix_items_title"), "items", ["title"], unique=False)

    op.drop_constraint(
        "fk_productos_categoria_id_categorias",
        "productos",
        type_="foreignkey",
    )
    op.drop_column("productos", "categoria_id")
    op.drop_index(op.f("ix_categorias_nombre"), table_name="categorias")
    op.drop_index(op.f("ix_categorias_id"), table_name="categorias")
    op.drop_table("categorias")
