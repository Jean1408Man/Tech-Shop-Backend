from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import relationship

from app.core.database import Base


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(
        DateTime().with_variant(mysql.TIMESTAMP(fsp=6), "mysql"),
        default=utc_now_naive,
        nullable=False,
    )
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(30), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)

    productos = relationship(
        "PedidoProducto",
        cascade="all, delete-orphan",
        back_populates="pedido",
    )
    combos = relationship(
        "PedidoCombo",
        cascade="all, delete-orphan",
        back_populates="pedido",
    )


class PedidoProducto(Base):
    __tablename__ = "pedido_productos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(
        Integer,
        ForeignKey("pedidos.id", ondelete="CASCADE"),
        nullable=False,
    )
    producto_id = Column(
        Integer,
        ForeignKey("productos.id", ondelete="SET NULL"),
        nullable=True,
    )
    oferta_id = Column(
        Integer,
        ForeignKey("ofertas.id", ondelete="SET NULL"),
        nullable=True,
    )
    cantidad = Column(Integer, nullable=False)
    producto_nombre = Column(String(100), nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    oferta_nombre = Column(String(100), nullable=True)
    descuento_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="productos")
    producto = relationship("Producto")
    oferta = relationship("Oferta")


class PedidoCombo(Base):
    __tablename__ = "pedido_combos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(
        Integer,
        ForeignKey("pedidos.id", ondelete="CASCADE"),
        nullable=False,
    )
    combo_id = Column(
        Integer,
        ForeignKey("combos.id", ondelete="SET NULL"),
        nullable=True,
    )
    cantidad = Column(Integer, nullable=False)
    combo_nombre = Column(String(100), nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="combos")
    combo = relationship("Combo")
