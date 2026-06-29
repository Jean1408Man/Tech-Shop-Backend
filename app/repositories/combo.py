from typing import Optional

from sqlalchemy.orm import Session, selectinload

from app.core.base.repository import BaseRepository
from app.models.combo import Combo


class ComboRepository(BaseRepository[Combo]):
    """Repository for Combo model database operations."""

    def __init__(self, db: Session):
        super().__init__(Combo, db)

    def get_with_productos(self, id: int) -> Optional[Combo]:
        return (
            self.db.query(Combo)
            .options(selectinload(Combo.productos))
            .filter(Combo.id == id)
            .first()
        )

    def get_all_with_productos(self, skip: int = 0, limit: int = 100):
        return (
            self.db.query(Combo)
            .options(selectinload(Combo.productos))
            .offset(skip)
            .limit(limit)
            .all()
        )
