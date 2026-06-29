from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.resumen import ProductoResumen


class OfertaBase(BaseModel):
    fecha_inicio: datetime
    fecha_fin: datetime
    nombre: str
    descripcion: Optional[str] = None
    monto_descuento: Decimal = Field(ge=0)


class OfertaCreate(OfertaBase):
    producto_ids: List[int] = Field(default_factory=list)


class OfertaUpdate(BaseModel):
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    monto_descuento: Optional[Decimal] = Field(default=None, ge=0)
    producto_ids: Optional[List[int]] = None


class Oferta(OfertaBase):
    id: int
    fecha_creacion: datetime
    productos: List[ProductoResumen] = Field(default_factory=list)

    class Config:
        from_attributes = True
