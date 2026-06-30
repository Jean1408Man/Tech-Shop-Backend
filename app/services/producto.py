from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.core.base.service import BaseService
from app.models.producto import Producto
from app.repositories.categoria import CategoriaRepository
from app.repositories.producto import ProductoRepository


class ProductoService(BaseService[ProductoRepository]):
    """Domain service for product business logic."""

    def __init__(self, db: Session):
        super().__init__(ProductoRepository(db))
        self.categoria_repository = CategoriaRepository(db)

    def _set_oferta_actual(self, producto: Optional[Producto]) -> Optional[Producto]:
        if producto:
            producto.oferta_actual = self.repository.get_current_offer(producto.id)
        return producto

    def get_by_id(self, producto_id: int) -> Optional[Producto]:
        return self._set_oferta_actual(self.repository.get_with_categoria(producto_id))

    def get_all(self, skip: int = 0, limit: int = 100):
        productos = self.repository.get_all_with_categoria(skip=skip, limit=limit)
        for producto in productos:
            self._set_oferta_actual(producto)
        return productos

    def _validate_categoria(self, categoria_id: int) -> None:
        if not self.categoria_repository.get(categoria_id):
            raise ValueError("Categoria no encontrada.")

    def create(
        self,
        nombre: str,
        precio_base: Decimal,
        categoria_id: int,
        descripcion: Optional[str] = None,
        url_img: Optional[str] = None,
    ) -> Producto:
        self._validate_categoria(categoria_id)
        producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio_base=precio_base,
            url_img=url_img,
            categoria_id=categoria_id,
        )
        return self._set_oferta_actual(self.repository.create(producto))

    def update(self, producto: Producto, **fields) -> Producto:
        if "categoria_id" in fields and fields["categoria_id"] is not None:
            self._validate_categoria(fields["categoria_id"])

        for key, value in fields.items():
            if value is not None:
                setattr(producto, key, value)
        return self._set_oferta_actual(self.repository.update(producto))

    def delete(self, producto: Producto) -> Producto:
        return self.repository.delete(producto)
