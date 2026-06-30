from typing import Optional

from sqlalchemy.orm import Session

from app.core.base.service import BaseService
from app.models.categoria import Categoria
from app.repositories.categoria import CategoriaRepository


class CategoriaService(BaseService[CategoriaRepository]):
    """Domain service for category business logic."""

    def __init__(self, db: Session):
        super().__init__(CategoriaRepository(db))

    def get_by_id(self, categoria_id: int) -> Optional[Categoria]:
        return self.repository.get_with_productos(categoria_id)

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.repository.get_all_with_productos(skip=skip, limit=limit)

    def create(
        self,
        nombre: str,
        url_img: Optional[str] = None,
        descripcion: Optional[str] = None,
    ) -> Categoria:
        categoria = Categoria(
            nombre=nombre,
            url_img=url_img,
            descripcion=descripcion,
        )
        return self.repository.create(categoria)

    def update(self, categoria: Categoria, **fields) -> Categoria:
        for key, value in fields.items():
            if value is not None:
                setattr(categoria, key, value)
        return self.repository.update(categoria)

    def delete(self, categoria: Categoria) -> Categoria:
        if categoria.productos:
            raise ValueError(
                "No se puede eliminar una categoria con productos asociados."
            )
        return self.repository.delete(categoria)
