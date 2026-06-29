from dataclasses import dataclass
from typing import List, Optional

from app.core.base.use_case import BaseQuery
from app.models.oferta import Oferta
from app.services.oferta import OfertaService


@dataclass
class GetOfertaByIdQuery(BaseQuery[Optional[Oferta]]):
    oferta_id: int
    service: OfertaService

    def execute(self) -> Optional[Oferta]:
        return self.service.get_by_id(self.oferta_id)


@dataclass
class ListOfertasQuery(BaseQuery[List[Oferta]]):
    service: OfertaService
    skip: int = 0
    limit: int = 100

    def execute(self) -> List[Oferta]:
        return self.service.get_all(skip=self.skip, limit=self.limit)
