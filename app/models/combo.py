from sqlalchemy import Column, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.associations import producto_combo


class Combo(Base):
    __tablename__ = "combos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Numeric(10, 2), nullable=False)
    imagen = Column(String(500), nullable=True)

    productos = relationship(
        "Producto",
        secondary=producto_combo,
        back_populates="combos",
    )
