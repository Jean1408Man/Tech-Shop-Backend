from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, Optional

from app.core.base.use_case import BaseCommand
from app.models.producto import Producto
from app.services.producto import ProductoService


@dataclass
class CreateProductoCommand(BaseCommand[Producto]):
    nombre: str
    precio_base: Decimal
    service: ProductoService
    descripcion: Optional[str] = None
    url_img: Optional[str] = None

    def execute(self) -> Producto:
        return self.service.create(
            nombre=self.nombre,
            descripcion=self.descripcion,
            precio_base=self.precio_base,
            url_img=self.url_img,
        )


@dataclass
class UpdateProductoCommand(BaseCommand[Producto]):
    producto: Producto
    service: ProductoService
    fields: Dict[str, Any] = field(default_factory=dict)

    def execute(self) -> Producto:
        return self.service.update(self.producto, **self.fields)


@dataclass
class DeleteProductoCommand(BaseCommand[Producto]):
    producto: Producto
    service: ProductoService

    def execute(self) -> Producto:
        return self.service.delete(self.producto)
