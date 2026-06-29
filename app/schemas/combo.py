from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.resumen import ProductoResumen


class ComboBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: Decimal = Field(ge=0)


class ComboCreate(ComboBase):
    producto_ids: List[int] = Field(default_factory=list)


class ComboUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[Decimal] = Field(default=None, ge=0)
    producto_ids: Optional[List[int]] = None


class Combo(ComboBase):
    id: int
    productos: List[ProductoResumen] = Field(default_factory=list)

    class Config:
        from_attributes = True
