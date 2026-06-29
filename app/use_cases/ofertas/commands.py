from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.core.base.use_case import BaseCommand
from app.models.oferta import Oferta
from app.services.oferta import OfertaService


@dataclass
class CreateOfertaCommand(BaseCommand[Oferta]):
    fecha_inicio: datetime
    fecha_fin: datetime
    nombre: str
    monto_descuento: Decimal
    service: OfertaService
    descripcion: Optional[str] = None
    producto_ids: Optional[List[int]] = None

    def execute(self) -> Oferta:
        return self.service.create(
            fecha_inicio=self.fecha_inicio,
            fecha_fin=self.fecha_fin,
            nombre=self.nombre,
            descripcion=self.descripcion,
            monto_descuento=self.monto_descuento,
            producto_ids=self.producto_ids,
        )


@dataclass
class UpdateOfertaCommand(BaseCommand[Oferta]):
    oferta: Oferta
    service: OfertaService
    fields: Dict[str, Any] = field(default_factory=dict)

    def execute(self) -> Oferta:
        return self.service.update(self.oferta, **self.fields)


@dataclass
class DeleteOfertaCommand(BaseCommand[Oferta]):
    oferta: Oferta
    service: OfertaService

    def execute(self) -> Oferta:
        return self.service.delete(self.oferta)
