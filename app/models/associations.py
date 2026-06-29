from sqlalchemy import Column, ForeignKey, Integer, Table

from app.core.database import Base


producto_oferta = Table(
    "producto_oferta",
    Base.metadata,
    Column(
        "producto_id",
        Integer,
        ForeignKey("productos.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "oferta_id",
        Integer,
        ForeignKey("ofertas.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

producto_combo = Table(
    "producto_combo",
    Base.metadata,
    Column(
        "producto_id",
        Integer,
        ForeignKey("productos.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "combo_id",
        Integer,
        ForeignKey("combos.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
