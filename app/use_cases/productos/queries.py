from dataclasses import dataclass
from typing import List, Optional

from app.core.base.use_case import BaseQuery
from app.models.producto import Producto
from app.services.producto import ProductoService


@dataclass
class GetProductoByIdQuery(BaseQuery[Optional[Producto]]):
    producto_id: int
    service: ProductoService

    def execute(self) -> Optional[Producto]:
        return self.service.get_by_id(self.producto_id)


@dataclass
class ListProductosQuery(BaseQuery[List[Producto]]):
    service: ProductoService
    skip: int = 0
    limit: int = 100

    def execute(self) -> List[Producto]:
        return self.service.get_all(skip=self.skip, limit=self.limit)
