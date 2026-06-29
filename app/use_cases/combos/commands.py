from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.core.base.use_case import BaseCommand
from app.models.combo import Combo
from app.services.combo import ComboService


@dataclass
class CreateComboCommand(BaseCommand[Combo]):
    nombre: str
    precio: Decimal
    service: ComboService
    descripcion: Optional[str] = None
    imagen: Optional[str] = None
    producto_ids: Optional[List[int]] = None

    def execute(self) -> Combo:
        return self.service.create(
            nombre=self.nombre,
            descripcion=self.descripcion,
            precio=self.precio,
            imagen=self.imagen,
            producto_ids=self.producto_ids,
        )


@dataclass
class UpdateComboCommand(BaseCommand[Combo]):
    combo: Combo
    service: ComboService
    fields: Dict[str, Any] = field(default_factory=dict)

    def execute(self) -> Combo:
        return self.service.update(self.combo, **self.fields)


@dataclass
class DeleteComboCommand(BaseCommand[Combo]):
    combo: Combo
    service: ComboService

    def execute(self) -> Combo:
        return self.service.delete(self.combo)
