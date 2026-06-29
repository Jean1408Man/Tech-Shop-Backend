from sqlalchemy import Column, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.associations import producto_combo, producto_oferta


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    precio_base = Column(Numeric(10, 2), nullable=False)
    url_img = Column(String(500), nullable=True)

    ofertas = relationship(
        "Oferta",
        secondary=producto_oferta,
        back_populates="productos",
    )
    combos = relationship(
        "Combo",
        secondary=producto_combo,
        back_populates="productos",
    )
