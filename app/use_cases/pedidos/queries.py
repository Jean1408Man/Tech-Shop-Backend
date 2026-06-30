from dataclasses import dataclass
from typing import List, Optional

from app.core.base.use_case import BaseQuery
from app.models.pedido import Pedido
from app.services.pedido import PedidoService


@dataclass
class GetPedidoByIdQuery(BaseQuery[Optional[Pedido]]):
    pedido_id: int
    service: PedidoService

    def execute(self) -> Optional[Pedido]:
        return self.service.get_by_id(self.pedido_id)


@dataclass
class ListPedidosQuery(BaseQuery[List[Pedido]]):
    service: PedidoService
    skip: int = 0
    limit: int = 100

    def execute(self) -> List[Pedido]:
        return self.service.get_all(skip=self.skip, limit=self.limit)
