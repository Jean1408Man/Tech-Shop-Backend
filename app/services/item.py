from sqlalchemy.orm import Session

from app.core.base.service import BaseService
from app.repositories.item import ItemRepository
from app.models.item import Item

class ItemService(BaseService[ItemRepository]):
    """Domain service for item business logic."""

    def __init__(self, db: Session):
        super().__init__(ItemRepository(db))

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.repository.get_all(skip=skip, limit=limit)

    def create(self, title: str, description: str = None) -> Item:
        item = Item(title=title, description=description)
        return self.repository.create(item)
