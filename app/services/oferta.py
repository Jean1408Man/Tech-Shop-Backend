from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.base.service import BaseService
from app.models.oferta import Oferta
from app.models.producto import Producto
from app.repositories.oferta import OfertaRepository
from app.repositories.producto import ProductoRepository


class OfertaService(BaseService[OfertaRepository]):
    """Domain service for offer business logic."""

    def __init__(self, db: Session):
        super().__init__(OfertaRepository(db))
        self.producto_repository = ProductoRepository(db)

    def _normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def _validate_dates(self, fecha_inicio: datetime, fecha_fin: datetime) -> None:
        if fecha_fin < fecha_inicio:
            raise ValueError("La fecha fin debe ser mayor o igual que la fecha inicio.")

    def _get_productos(self, producto_ids: Optional[List[int]]) -> List[Producto]:
        if not producto_ids:
            return []

        productos = self.producto_repository.get_by_ids(producto_ids)
        found_ids = {producto.id for producto in productos}
        missing_ids = sorted(set(producto_ids) - found_ids)
        if missing_ids:
            raise ValueError(f"Productos no encontrados: {missing_ids}.")
        return productos

    def get_by_id(self, oferta_id: int) -> Optional[Oferta]:
        return self.repository.get_with_productos(oferta_id)

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.repository.get_all_with_productos(skip=skip, limit=limit)

    def create(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        nombre: str,
        monto_descuento: Decimal,
        descripcion: Optional[str] = None,
        imagen: Optional[str] = None,
        producto_ids: Optional[List[int]] = None,
    ) -> Oferta:
        fecha_inicio = self._normalize_datetime(fecha_inicio)
        fecha_fin = self._normalize_datetime(fecha_fin)
        self._validate_dates(fecha_inicio, fecha_fin)

        oferta = Oferta(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            nombre=nombre,
            descripcion=descripcion,
            monto_descuento=monto_descuento,
            imagen=imagen,
        )
        oferta.productos = self._get_productos(producto_ids)
        return self.repository.create(oferta)

    def update(self, oferta: Oferta, **fields) -> Oferta:
        if "fecha_inicio" in fields and fields["fecha_inicio"] is not None:
            fields["fecha_inicio"] = self._normalize_datetime(fields["fecha_inicio"])
        if "fecha_fin" in fields and fields["fecha_fin"] is not None:
            fields["fecha_fin"] = self._normalize_datetime(fields["fecha_fin"])

        fecha_inicio = fields.get("fecha_inicio", oferta.fecha_inicio)
        fecha_fin = fields.get("fecha_fin", oferta.fecha_fin)
        self._validate_dates(fecha_inicio, fecha_fin)

        if "producto_ids" in fields:
            oferta.productos = self._get_productos(fields.pop("producto_ids"))

        for key, value in fields.items():
            if value is not None:
                setattr(oferta, key, value)
        return self.repository.update(oferta)

    def delete(self, oferta: Oferta) -> Oferta:
        return self.repository.delete(oferta)
