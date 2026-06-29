from typing import Optional
from dataclasses import dataclass

from app.core.base.use_case import BaseCommand
from app.models.item import Item
from app.services.item import ItemService


@dataclass
class CreateItemCommand(BaseCommand[Item]):
    title: str
    service: ItemService
    description: Optional[str] = None

    def execute(self) -> Item:
        return self.service.create(title=self.title, description=self.description)
