from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from app.core.base.repository import BaseRepository
from app.models.associations import producto_oferta
from app.models.oferta import Oferta
from app.models.producto import Producto


class ProductoRepository(BaseRepository[Producto]):
    """Repository for Producto model database operations."""

    def __init__(self, db: Session):
        super().__init__(Producto, db)

    def get_by_ids(self, ids: List[int]) -> List[Producto]:
        if not ids:
            return []
        return self.db.query(Producto).filter(Producto.id.in_(ids)).all()

    def get_current_offer(self, producto_id: int) -> Oferta | None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return (
            self.db.query(Oferta)
            .join(producto_oferta, Oferta.id == producto_oferta.c.oferta_id)
            .filter(
                producto_oferta.c.producto_id == producto_id,
                Oferta.fecha_inicio <= now,
                Oferta.fecha_fin >= now,
            )
            .order_by(Oferta.fecha_creacion.desc())
            .first()
        )
