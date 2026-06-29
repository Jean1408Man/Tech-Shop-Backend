from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ProductoResumen(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio_base: Decimal
    url_img: Optional[str] = None

    class Config:
        from_attributes = True


class OfertaResumen(BaseModel):
    id: int
    fecha_creacion: datetime
    fecha_inicio: datetime
    fecha_fin: datetime
    nombre: str
    descripcion: Optional[str] = None
    monto_descuento: Decimal
    imagen: Optional[str] = None

    class Config:
        from_attributes = True
