from dataclasses import dataclass
from typing import List, Optional

from app.core.base.use_case import BaseQuery
from app.models.combo import Combo
from app.services.combo import ComboService


@dataclass
class GetComboByIdQuery(BaseQuery[Optional[Combo]]):
    combo_id: int
    service: ComboService

    def execute(self) -> Optional[Combo]:
        return self.service.get_by_id(self.combo_id)


@dataclass
class ListCombosQuery(BaseQuery[List[Combo]]):
    service: ComboService
    skip: int = 0
    limit: int = 100

    def execute(self) -> List[Combo]:
        return self.service.get_all(skip=self.skip, limit=self.limit)
