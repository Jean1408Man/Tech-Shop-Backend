from typing import List
from dataclasses import dataclass

from app.core.base.use_case import BaseQuery
from app.models.item import Item
from app.services.item import ItemService


@dataclass
class ListItemsQuery(BaseQuery[List[Item]]):
    service: ItemService
    skip: int = 0
    limit: int = 100

    def execute(self) -> List[Item]:
        return self.service.get_all(skip=self.skip, limit=self.limit)
