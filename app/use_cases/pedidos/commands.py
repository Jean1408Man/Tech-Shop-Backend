from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.core.base.use_case import BaseCommand
from app.models.pedido import Pedido
from app.services.pedido import PedidoService


@dataclass
class CreatePedidoCommand(BaseCommand[Pedido]):
    nombre: str
    telefono: str
    service: PedidoService
    productos: Optional[List[dict[str, Any]]] = None
    combos: Optional[List[dict[str, Any]]] = None

    def execute(self) -> Pedido:
        return self.service.create(
            nombre=self.nombre,
            telefono=self.telefono,
            productos=self.productos,
            combos=self.combos,
        )


@dataclass
class UpdatePedidoCommand(BaseCommand[Pedido]):
    pedido: Pedido
    service: PedidoService
    fields: Dict[str, Any] = field(default_factory=dict)

    def execute(self) -> Pedido:
        return self.service.update(self.pedido, **self.fields)


@dataclass
class DeletePedidoCommand(BaseCommand[Pedido]):
    pedido: Pedido
    service: PedidoService

    def execute(self) -> Pedido:
        return self.service.delete(self.pedido)
