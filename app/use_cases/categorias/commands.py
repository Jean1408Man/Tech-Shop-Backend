from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.core.base.use_case import BaseCommand
from app.models.categoria import Categoria
from app.services.categoria import CategoriaService


@dataclass
class CreateCategoriaCommand(BaseCommand[Categoria]):
    nombre: str
    service: CategoriaService
    url_img: Optional[str] = None
    descripcion: Optional[str] = None

    def execute(self) -> Categoria:
        return self.service.create(
            nombre=self.nombre,
            url_img=self.url_img,
            descripcion=self.descripcion,
        )


@dataclass
class UpdateCategoriaCommand(BaseCommand[Categoria]):
    categoria: Categoria
    service: CategoriaService
    fields: Dict[str, Any] = field(default_factory=dict)

    def execute(self) -> Categoria:
        return self.service.update(self.categoria, **self.fields)


@dataclass
class DeleteCategoriaCommand(BaseCommand[Categoria]):
    categoria: Categoria
    service: CategoriaService

    def execute(self) -> Categoria:
        return self.service.delete(self.categoria)
