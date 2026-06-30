from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class PedidoProductoInput(BaseModel):
    producto_id: int
    cantidad: int = Field(ge=1)
    oferta_id: Optional[int] = None


class PedidoComboInput(BaseModel):
    combo_id: int
    cantidad: int = Field(ge=1)


class PedidoBase(BaseModel):
    nombre: str
    telefono: str


class PedidoCreate(PedidoBase):
    productos: List[PedidoProductoInput] = Field(default_factory=list)
    combos: List[PedidoComboInput] = Field(default_factory=list)


class PedidoUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    productos: Optional[List[PedidoProductoInput]] = None
    combos: Optional[List[PedidoComboInput]] = None


class PedidoProducto(BaseModel):
    id: int
    producto_id: Optional[int] = None
    oferta_id: Optional[int] = None
    cantidad: int
    producto_nombre: str
    precio_unitario: Decimal
    oferta_nombre: Optional[str] = None
    descuento_unitario: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True


class PedidoCombo(BaseModel):
    id: int
    combo_id: Optional[int] = None
    cantidad: int
    combo_nombre: str
    precio_unitario: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True


class Pedido(PedidoBase):
    id: int
    fecha: datetime
    total: Decimal
    productos: List[PedidoProducto] = Field(default_factory=list)
    combos: List[PedidoCombo] = Field(default_factory=list)

    class Config:
        from_attributes = True
