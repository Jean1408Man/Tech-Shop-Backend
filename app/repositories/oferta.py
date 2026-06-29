from typing import Optional

from sqlalchemy.orm import Session, selectinload

from app.core.base.repository import BaseRepository
from app.models.oferta import Oferta


class OfertaRepository(BaseRepository[Oferta]):
    """Repository for Oferta model database operations."""

    def __init__(self, db: Session):
        super().__init__(Oferta, db)

    def get_with_productos(self, id: int) -> Optional[Oferta]:
        return (
            self.db.query(Oferta)
            .options(selectinload(Oferta.productos))
            .filter(Oferta.id == id)
            .first()
        )

    def get_all_with_productos(self, skip: int = 0, limit: int = 100):
        return (
            self.db.query(Oferta)
            .options(selectinload(Oferta.productos))
            .offset(skip)
            .limit(limit)
            .all()
        )
