from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.base.service import BaseService
from app.models.combo import Combo
from app.models.producto import Producto
from app.repositories.combo import ComboRepository
from app.repositories.producto import ProductoRepository


class ComboService(BaseService[ComboRepository]):
    """Domain service for combo business logic."""

    def __init__(self, db: Session):
        super().__init__(ComboRepository(db))
        self.producto_repository = ProductoRepository(db)

    def _get_productos(self, producto_ids: Optional[List[int]]) -> List[Producto]:
        if not producto_ids:
            return []

        productos = self.producto_repository.get_by_ids(producto_ids)
        found_ids = {producto.id for producto in productos}
        missing_ids = sorted(set(producto_ids) - found_ids)
        if missing_ids:
            raise ValueError(f"Productos no encontrados: {missing_ids}.")
        return productos

    def get_by_id(self, combo_id: int) -> Optional[Combo]:
        return self.repository.get_with_productos(combo_id)

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.repository.get_all_with_productos(skip=skip, limit=limit)

    def create(
        self,
        nombre: str,
        precio: Decimal,
        descripcion: Optional[str] = None,
        producto_ids: Optional[List[int]] = None,
    ) -> Combo:
        combo = Combo(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
        )
        combo.productos = self._get_productos(producto_ids)
        return self.repository.create(combo)

    def update(self, combo: Combo, **fields) -> Combo:
        if "producto_ids" in fields:
            combo.productos = self._get_productos(fields.pop("producto_ids"))

        for key, value in fields.items():
            if value is not None:
                setattr(combo, key, value)
        return self.repository.update(combo)

    def delete(self, combo: Combo) -> Combo:
        return self.repository.delete(combo)
