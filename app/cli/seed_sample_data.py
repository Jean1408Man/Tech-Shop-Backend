import argparse
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.cli.reset_database import reset_database
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.categoria import Categoria
from app.models.combo import Combo
from app.models.oferta import Oferta
from app.models.pedido import Pedido
from app.models.producto import Producto
from app.models.user import User
from app.services.pedido import PedidoService


DEMO_EMAIL = "demo@orbita.local"
DEMO_PASSWORD = "demo123"


def _has_existing_data(db: Session) -> bool:
    models = [User, Categoria, Producto, Oferta, Combo, Pedido]
    return any((db.scalar(select(func.count()).select_from(model)) or 0) for model in models)


def seed_sample_data(*, reset: bool = False, confirm_reset: bool = False, append: bool = False) -> None:
    if reset:
        reset_database(confirm=confirm_reset)

    with SessionLocal() as db:
        if not append and _has_existing_data(db):
            raise ValueError(
                "La base ya tiene datos. Usa --reset --yes para reemplazarlos "
                "o --append para agregar datos encima."
            )

        bebidas = Categoria(
            nombre="Bebidas",
            descripcion="Bebidas frias y calientes.",
            url_img="https://images.unsplash.com/photo-1495474472287-4d71bcdd2085",
        )
        panaderia = Categoria(
            nombre="Panaderia",
            descripcion="Panes, bocaditos y desayunos.",
            url_img="https://images.unsplash.com/photo-1509440159596-0249088772ff",
        )
        postres = Categoria(
            nombre="Postres",
            descripcion="Dulces y postres caseros.",
            url_img="https://images.unsplash.com/photo-1488477181946-6428a0291777",
        )
        db.add_all([bebidas, panaderia, postres])
        db.flush()

        cafe = Producto(
            nombre="Cafe cubano",
            descripcion="Cafe intenso servido corto.",
            precio_base=Decimal("10.00"),
            url_img="https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd",
            categoria_id=bebidas.id,
        )
        jugo = Producto(
            nombre="Jugo natural",
            descripcion="Jugo de frutas de temporada.",
            precio_base=Decimal("8.00"),
            url_img="https://images.unsplash.com/photo-1622597467836-f3285f2131b8",
            categoria_id=bebidas.id,
        )
        pan = Producto(
            nombre="Pan con tortilla",
            descripcion="Pan suave con tortilla recien hecha.",
            precio_base=Decimal("15.00"),
            url_img="https://images.unsplash.com/photo-1528735602780-2552fd46c7af",
            categoria_id=panaderia.id,
        )
        pastel = Producto(
            nombre="Pastel de guayaba",
            descripcion="Pastel dulce relleno de guayaba.",
            precio_base=Decimal("7.50"),
            url_img="https://images.unsplash.com/photo-1486427944299-d1955d23e34d",
            categoria_id=postres.id,
        )
        flan = Producto(
            nombre="Flan casero",
            descripcion="Flan tradicional con caramelo.",
            precio_base=Decimal("9.00"),
            url_img="https://images.unsplash.com/photo-1551024506-0bccd828d307",
            categoria_id=postres.id,
        )
        db.add_all([cafe, jugo, pan, pastel, flan])
        db.flush()

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        cafe_offer = Oferta(
            fecha_inicio=now - timedelta(days=1),
            fecha_fin=now + timedelta(days=14),
            nombre="Cafe feliz",
            descripcion="Descuento temporal para cafe cubano.",
            monto_descuento=Decimal("2.00"),
            imagen="https://images.unsplash.com/photo-1509042239860-f550ce710b93",
        )
        cafe_offer.productos = [cafe]
        desayuno_offer = Oferta(
            fecha_inicio=now - timedelta(days=1),
            fecha_fin=now + timedelta(days=7),
            nombre="Desayuno rapido",
            descripcion="Descuento para pan con tortilla.",
            monto_descuento=Decimal("3.00"),
            imagen="https://images.unsplash.com/photo-1533089860892-a7c6f0a88666",
        )
        desayuno_offer.productos = [pan]
        db.add_all([cafe_offer, desayuno_offer])

        desayuno_combo = Combo(
            nombre="Combo desayuno",
            descripcion="Cafe cubano y pan con tortilla.",
            precio=Decimal("22.00"),
            imagen="https://images.unsplash.com/photo-1533089860892-a7c6f0a88666",
        )
        desayuno_combo.productos = [cafe, pan]
        merienda_combo = Combo(
            nombre="Combo merienda",
            descripcion="Jugo natural y pastel de guayaba.",
            precio=Decimal("14.00"),
            imagen="https://images.unsplash.com/photo-1499636136210-6f4ee915583e",
        )
        merienda_combo.productos = [jugo, pastel]
        db.add_all([desayuno_combo, merienda_combo])

        demo_user = User(
            email=DEMO_EMAIL,
            hashed_password=get_password_hash(DEMO_PASSWORD),
            full_name="Usuario Demo",
            is_active=True,
        )
        db.add(demo_user)
        db.commit()

        pedido_service = PedidoService(db)
        pedido_service.create(
            nombre="Ana Demo",
            telefono="55512345",
            productos=[
                {"producto_id": cafe.id, "cantidad": 2},
                {"producto_id": pastel.id, "cantidad": 3},
            ],
            combos=[{"combo_id": desayuno_combo.id, "cantidad": 1}],
        )

    print("Datos de ejemplo creados.")
    print(f"Usuario demo: {DEMO_EMAIL}")
    print(f"Password demo: {DEMO_PASSWORD}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Llena la base de datos con datos de ejemplo para frontend.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Vacia la base antes de sembrar datos.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirma el reset cuando se usa --reset.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Agrega datos aunque la base ya tenga contenido.",
    )
    args = parser.parse_args()

    seed_sample_data(reset=args.reset, confirm_reset=args.yes, append=args.append)


if __name__ == "__main__":
    main()
