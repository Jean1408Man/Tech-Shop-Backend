from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.core.base.service import BaseService
from app.models.producto import Producto
from app.repositories.producto import ProductoRepository


class ProductoService(BaseService[ProductoRepository]):
    """Domain service for product business logic."""

    def __init__(self, db: Session):
        super().__init__(ProductoRepository(db))

    def _set_oferta_actual(self, producto: Optional[Producto]) -> Optional[Producto]:
        if producto:
            producto.oferta_actual = self.repository.get_current_offer(producto.id)
        return producto

    def get_by_id(self, producto_id: int) -> Optional[Producto]:
        return self._set_oferta_actual(self.repository.get(producto_id))

    def get_all(self, skip: int = 0, limit: int = 100):
        productos = self.repository.get_all(skip=skip, limit=limit)
        for producto in productos:
            self._set_oferta_actual(producto)
        return productos

    def create(
        self,
        nombre: str,
        precio_base: Decimal,
        descripcion: Optional[str] = None,
        url_img: Optional[str] = None,
    ) -> Producto:
        producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio_base=precio_base,
            url_img=url_img,
        )
        return self._set_oferta_actual(self.repository.create(producto))

    def update(self, producto: Producto, **fields) -> Producto:
        for key, value in fields.items():
            if value is not None:
                setattr(producto, key, value)
        return self._set_oferta_actual(self.repository.update(producto))

    def delete(self, producto: Producto) -> Producto:
        return self.repository.delete(producto)
