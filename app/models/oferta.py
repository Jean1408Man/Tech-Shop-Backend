from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.associations import producto_oferta


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Oferta(Base):
    __tablename__ = "ofertas"

    id = Column(Integer, primary_key=True, index=True)
    fecha_creacion = Column(
        DateTime().with_variant(mysql.TIMESTAMP(fsp=6), "mysql"),
        default=utc_now_naive,
        nullable=False,
    )
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    nombre = Column(String(100), index=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    monto_descuento = Column(Numeric(10, 2), nullable=False)
    imagen = Column(String(500), nullable=True)

    productos = relationship(
        "Producto",
        secondary=producto_oferta,
        back_populates="ofertas",
    )
