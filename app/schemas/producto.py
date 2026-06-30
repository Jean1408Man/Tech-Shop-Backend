from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.resumen import CategoriaResumen, OfertaResumen


class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_base: Decimal = Field(ge=0)
    url_img: Optional[str] = None
    categoria_id: int


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[Decimal] = Field(default=None, ge=0)
    url_img: Optional[str] = None
    categoria_id: Optional[int] = None


class Producto(ProductoBase):
    id: int
    categoria: CategoriaResumen
    oferta_actual: Optional[OfertaResumen] = None

    class Config:
        from_attributes = True
