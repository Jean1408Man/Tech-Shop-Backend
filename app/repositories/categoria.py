from typing import Optional

from sqlalchemy.orm import Session, selectinload

from app.core.base.repository import BaseRepository
from app.models.categoria import Categoria


class CategoriaRepository(BaseRepository[Categoria]):
    """Repository for Categoria model database operations."""

    def __init__(self, db: Session):
        super().__init__(Categoria, db)

    def get_with_productos(self, id: int) -> Optional[Categoria]:
        return (
            self.db.query(Categoria)
            .options(selectinload(Categoria.productos))
            .filter(Categoria.id == id)
            .first()
        )

    def get_all_with_productos(self, skip: int = 0, limit: int = 100):
        return (
            self.db.query(Categoria)
            .options(selectinload(Categoria.productos))
            .offset(skip)
            .limit(limit)
            .all()
        )
