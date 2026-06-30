from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, List, Optional

from sqlalchemy.orm import Session

from app.core.base.service import BaseService
from app.models.combo import Combo
from app.models.oferta import Oferta
from app.models.pedido import Pedido, PedidoCombo, PedidoProducto
from app.models.producto import Producto
from app.repositories.combo import ComboRepository
from app.repositories.oferta import OfertaRepository
from app.repositories.pedido import PedidoRepository
from app.repositories.producto import ProductoRepository


class PedidoService(BaseService[PedidoRepository]):
    """Domain service for order business logic."""

    def __init__(self, db: Session):
        super().__init__(PedidoRepository(db))
        self.producto_repository = ProductoRepository(db)
        self.oferta_repository = OfertaRepository(db)
        self.combo_repository = ComboRepository(db)

    def get_by_id(self, pedido_id: int) -> Optional[Pedido]:
        return self.repository.get_with_items(pedido_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Pedido]:
        return self.repository.get_all_with_items(skip=skip, limit=limit)

    def create(
        self,
        nombre: str,
        telefono: str,
        productos: Optional[List[dict[str, Any]]] = None,
        combos: Optional[List[dict[str, Any]]] = None,
    ) -> Pedido:
        fecha = datetime.now(timezone.utc).replace(tzinfo=None)
        pedido = Pedido(
            nombre=nombre,
            telefono=telefono,
            fecha=fecha,
            total=Decimal("0.00"),
        )
        pedido.productos = self._build_producto_lines(productos or [], fecha)
        pedido.combos = self._build_combo_lines(combos or [])
        self._recalculate_total(pedido)
        self._validate_has_items(pedido.productos, pedido.combos)
        return self.repository.create(pedido)

    def update(self, pedido: Pedido, **fields) -> Pedido:
        if "nombre" in fields and fields["nombre"] is not None:
            pedido.nombre = fields["nombre"]
        if "telefono" in fields and fields["telefono"] is not None:
            pedido.telefono = fields["telefono"]
        if "productos" in fields:
            pedido.productos = self._build_producto_lines(
                fields["productos"] or [],
                pedido.fecha,
            )
        if "combos" in fields:
            pedido.combos = self._build_combo_lines(fields["combos"] or [])

        self._recalculate_total(pedido)
        self._validate_has_items(pedido.productos, pedido.combos)
        return self.repository.update(pedido)

    def delete(self, pedido: Pedido) -> Pedido:
        return self.repository.delete(pedido)

    def _build_producto_lines(
        self,
        productos: List[dict[str, Any]],
        fecha: datetime,
    ) -> List[PedidoProducto]:
        return [self._build_producto_line(item, fecha) for item in productos]

    def _build_producto_line(
        self,
        item: dict[str, Any],
        fecha: datetime,
    ) -> PedidoProducto:
        cantidad = item["cantidad"]
        producto = self._get_producto(item["producto_id"])
        oferta = self._get_line_offer(producto, item.get("oferta_id"), fecha)
        descuento = self._get_discount(oferta)
        subtotal = self._calculate_subtotal(producto.precio_base, descuento, cantidad)

        return PedidoProducto(
            producto_id=producto.id,
            oferta_id=oferta.id if oferta else None,
            cantidad=cantidad,
            producto_nombre=producto.nombre,
            precio_unitario=producto.precio_base,
            oferta_nombre=oferta.nombre if oferta else None,
            descuento_unitario=descuento,
            subtotal=subtotal,
        )

    def _build_combo_lines(self, combos: List[dict[str, Any]]) -> List[PedidoCombo]:
        return [self._build_combo_line(item) for item in combos]

    def _build_combo_line(self, item: dict[str, Any]) -> PedidoCombo:
        cantidad = item["cantidad"]
        combo = self._get_combo(item["combo_id"])
        subtotal = self._calculate_subtotal(combo.precio, Decimal("0.00"), cantidad)

        return PedidoCombo(
            combo_id=combo.id,
            cantidad=cantidad,
            combo_nombre=combo.nombre,
            precio_unitario=combo.precio,
            subtotal=subtotal,
        )

    def _get_producto(self, producto_id: int) -> Producto:
        producto = self.producto_repository.get(producto_id)
        if not producto:
            raise ValueError("Producto no encontrado.")
        return producto

    def _get_combo(self, combo_id: int) -> Combo:
        combo = self.combo_repository.get(combo_id)
        if not combo:
            raise ValueError("Combo no encontrado.")
        return combo

    def _get_line_offer(
        self,
        producto: Producto,
        oferta_id: Optional[int],
        fecha: datetime,
    ) -> Optional[Oferta]:
        if oferta_id is None:
            return self.producto_repository.get_current_offer(producto.id)

        oferta = self.oferta_repository.get_with_productos(oferta_id)
        if not oferta:
            raise ValueError("Oferta no encontrada.")
        oferta_producto_ids = {
            oferta_producto.id for oferta_producto in oferta.productos
        }
        if producto.id not in oferta_producto_ids:
            raise ValueError("La oferta no pertenece al producto indicado.")
        if not self._is_offer_active(oferta, fecha):
            raise ValueError("La oferta no esta activa para la fecha del pedido.")
        return oferta

    def _is_offer_active(self, oferta: Oferta, fecha: datetime) -> bool:
        return oferta.fecha_inicio <= fecha <= oferta.fecha_fin

    def _get_discount(self, oferta: Optional[Oferta]) -> Decimal:
        if not oferta:
            return Decimal("0.00")
        return oferta.monto_descuento

    def _calculate_subtotal(
        self,
        precio_unitario: Decimal,
        descuento_unitario: Decimal,
        cantidad: int,
    ) -> Decimal:
        precio_final = max(precio_unitario - descuento_unitario, Decimal("0.00"))
        return (precio_final * cantidad).quantize(Decimal("0.01"))

    def _recalculate_total(self, pedido: Pedido) -> None:
        lineas = [linea.subtotal for linea in pedido.productos]
        lineas.extend(linea.subtotal for linea in pedido.combos)
        pedido.total = sum(lineas, Decimal("0.00")).quantize(Decimal("0.01"))

    def _validate_has_items(
        self,
        productos: List[PedidoProducto],
        combos: List[PedidoCombo],
    ) -> None:
        if not productos and not combos:
            raise ValueError("El pedido debe tener al menos un producto o combo.")
