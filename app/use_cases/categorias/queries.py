from dataclasses import dataclass
from typing import List, Optional

from app.core.base.use_case import BaseQuery
from app.models.categoria import Categoria
from app.services.categoria import CategoriaService


@dataclass
class GetCategoriaByIdQuery(BaseQuery[Optional[Categoria]]):
    categoria_id: int
    service: CategoriaService

    def execute(self) -> Optional[Categoria]:
        return self.service.get_by_id(self.categoria_id)


@dataclass
class ListCategoriasQuery(BaseQuery[List[Categoria]]):
    service: CategoriaService
    skip: int = 0
    limit: int = 100

    def execute(self) -> List[Categoria]:
        return self.service.get_all(skip=self.skip, limit=self.limit)
