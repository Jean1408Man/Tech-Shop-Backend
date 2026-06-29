from sqlalchemy.orm import Session

from app.core.base.repository import BaseRepository
from app.models.item import Item

class ItemRepository(BaseRepository[Item]):
    """Repository for Item model database operations."""

    def __init__(self, db: Session):
        super().__init__(Item, db)
