from typing import List, Optional

from sqlalchemy.orm import Session, selectinload

from app.core.base.repository import BaseRepository
from app.models.pedido import Pedido


class PedidoRepository(BaseRepository[Pedido]):
    """Repository for Pedido model database operations."""

    def __init__(self, db: Session):
        super().__init__(Pedido, db)

    def get_with_items(self, id: int) -> Optional[Pedido]:
        return (
            self.db.query(Pedido)
            .options(selectinload(Pedido.productos), selectinload(Pedido.combos))
            .filter(Pedido.id == id)
            .first()
        )

    def get_all_with_items(self, skip: int = 0, limit: int = 100) -> List[Pedido]:
        return (
            self.db.query(Pedido)
            .options(selectinload(Pedido.productos), selectinload(Pedido.combos))
            .offset(skip)
            .limit(limit)
            .all()
        )
