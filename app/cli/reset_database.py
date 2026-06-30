import argparse
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import delete, func, select, text
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.associations import producto_combo, producto_oferta
from app.models.categoria import Categoria
from app.models.combo import Combo
from app.models.oferta import Oferta
from app.models.pedido import Pedido, PedidoCombo, PedidoProducto
from app.models.producto import Producto
from app.models.user import User


@dataclass(frozen=True)
class ResetResult:
    table: str
    rows: int


def _count_rows(db: Session, model) -> int:
    return db.scalar(select(func.count()).select_from(model)) or 0


def _delete_model(db: Session, model) -> ResetResult:
    rows = _count_rows(db, model)
    db.execute(delete(model))
    return ResetResult(model.__tablename__, rows)


def _delete_table(db: Session, table) -> ResetResult:
    rows = db.scalar(select(func.count()).select_from(table)) or 0
    db.execute(table.delete())
    return ResetResult(table.name, rows)


def _reset_mysql_auto_increment(db: Session, table_names: Iterable[str]) -> None:
    if db.bind is None or db.bind.dialect.name != "mysql":
        return

    for table_name in table_names:
        db.execute(text(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1"))


def reset_database(*, confirm: bool, keep_users: bool = False) -> list[ResetResult]:
    if not confirm:
        raise ValueError("Use --yes para confirmar el vaciado de la base de datos.")

    results: list[ResetResult] = []
    with SessionLocal() as db:
        results.extend(
            [
                _delete_model(db, PedidoProducto),
                _delete_model(db, PedidoCombo),
                _delete_model(db, Pedido),
                _delete_table(db, producto_oferta),
                _delete_table(db, producto_combo),
                _delete_model(db, Oferta),
                _delete_model(db, Combo),
                _delete_model(db, Producto),
                _delete_model(db, Categoria),
            ]
        )
        if not keep_users:
            results.append(_delete_model(db, User))
        auto_increment_tables = [
            "pedido_productos",
            "pedido_combos",
            "pedidos",
            "ofertas",
            "combos",
            "productos",
            "categorias",
        ]
        if not keep_users:
            auto_increment_tables.append("users")
        _reset_mysql_auto_increment(db, auto_increment_tables)
        db.commit()
    return results


def _print_results(results: Iterable[ResetResult]) -> None:
    for result in results:
        print(f"{result.table}: {result.rows} filas eliminadas")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Vacia los datos de aplicacion sin tocar alembic_version.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirma la operacion destructiva.",
    )
    parser.add_argument(
        "--keep-users",
        action="store_true",
        help="Conserva usuarios registrados.",
    )
    args = parser.parse_args()

    results = reset_database(confirm=args.yes, keep_users=args.keep_users)
    _print_results(results)


if __name__ == "__main__":
    main()
