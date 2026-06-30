from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True, nullable=False)
    url_img = Column(String(500), nullable=True)
    descripcion = Column(Text, nullable=True)

    productos = relationship("Producto", back_populates="categoria")
