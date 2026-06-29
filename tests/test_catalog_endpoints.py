from datetime import datetime, timedelta, timezone
from decimal import Decimal
from time import sleep

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models, schemas
from app.api.endpoints import combos, ofertas, productos
from app.core.database import Base


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def create_producto(db, nombre="Cafe", precio_base="10.50"):
    return productos.create_producto(
        schemas.ProductoCreate(
            nombre=nombre,
            descripcion="Producto de prueba",
            precio_base=Decimal(precio_base),
            url_img="https://example.com/producto.png",
        ),
        db=db,
    )


def active_dates():
    now = datetime.now(timezone.utc)
    return {
        "fecha_inicio": now - timedelta(days=1),
        "fecha_fin": now + timedelta(days=1),
    }


def test_productos_crud(db):
    created = create_producto(db)
    created_schema = schemas.Producto.model_validate(created)
    assert created_schema.nombre == "Cafe"
    assert created_schema.precio_base == Decimal("10.50")
    assert created_schema.oferta_actual is None

    producto_id = created.id
    listed = productos.read_productos(db=db)
    assert [producto.id for producto in listed] == [producto_id]

    updated = productos.update_producto(
        producto_id,
        schemas.ProductoUpdate(nombre="Cafe premium", precio_base=Decimal("12.00")),
        db=db,
    )
    updated_schema = schemas.Producto.model_validate(updated)
    assert updated_schema.nombre == "Cafe premium"
    assert updated_schema.precio_base == Decimal("12.00")

    deleted = productos.delete_producto(producto_id, db=db)
    assert deleted.id == producto_id
    with pytest.raises(HTTPException) as exc_info:
        productos.read_producto(producto_id, db=db)
    assert exc_info.value.status_code == 404


def test_producto_uses_latest_active_offer_by_creation_timestamp(db):
    producto = create_producto(db)
    producto_id = producto.id

    first_offer = ofertas.create_oferta(
        schemas.OfertaCreate(
            **active_dates(),
            nombre="Oferta vigente vieja",
            descripcion="Primera oferta vigente",
            monto_descuento=Decimal("1.00"),
            producto_ids=[producto_id],
        ),
        db=db,
    )

    sleep(0.001)
    second_offer = ofertas.create_oferta(
        schemas.OfertaCreate(
            **active_dates(),
            nombre="Oferta vigente nueva",
            descripcion="Segunda oferta vigente",
            monto_descuento=Decimal("2.00"),
            producto_ids=[producto_id],
        ),
        db=db,
    )

    now = datetime.now(timezone.utc)
    future_offer = ofertas.create_oferta(
        schemas.OfertaCreate(
            fecha_inicio=now + timedelta(days=2),
            fecha_fin=now + timedelta(days=3),
            nombre="Oferta futura",
            descripcion="No debe aplicar todavia",
            monto_descuento=Decimal("9.00"),
            producto_ids=[producto_id],
        ),
        db=db,
    )
    assert future_offer.id is not None

    assert second_offer.fecha_creacion > first_offer.fecha_creacion
    assert second_offer.fecha_creacion.microsecond > 0

    producto_response = productos.read_producto(producto_id, db=db)
    producto_schema = schemas.Producto.model_validate(producto_response)
    assert producto_schema.oferta_actual.nombre == "Oferta vigente nueva"
    assert producto_schema.oferta_actual.monto_descuento == Decimal("2.00")


def test_ofertas_validate_product_ids_and_return_products(db):
    with pytest.raises(HTTPException) as exc_info:
        ofertas.create_oferta(
            schemas.OfertaCreate(
                **active_dates(),
                nombre="Oferta invalida",
                descripcion=None,
                monto_descuento=Decimal("3.00"),
                producto_ids=[999],
            ),
            db=db,
        )
    assert exc_info.value.status_code == 400

    producto = create_producto(db)
    valid_offer = ofertas.create_oferta(
        schemas.OfertaCreate(
            **active_dates(),
            nombre="Oferta valida",
            descripcion="Con productos",
            monto_descuento=Decimal("3.00"),
            producto_ids=[producto.id],
        ),
        db=db,
    )
    oferta_schema = schemas.Oferta.model_validate(valid_offer)
    assert [producto.id for producto in oferta_schema.productos] == [producto.id]


def test_combos_crud_with_products(db):
    producto_a = create_producto(db, nombre="Cafe", precio_base="10.00")
    producto_b = create_producto(db, nombre="Pan", precio_base="2.50")

    combo = combos.create_combo(
        schemas.ComboCreate(
            nombre="Desayuno",
            descripcion="Cafe con pan",
            precio=Decimal("11.00"),
            producto_ids=[producto_a.id, producto_b.id],
        ),
        db=db,
    )
    combo_schema = schemas.Combo.model_validate(combo)
    assert combo_schema.nombre == "Desayuno"
    assert {producto.id for producto in combo_schema.productos} == {
        producto_a.id,
        producto_b.id,
    }

    updated = combos.update_combo(
        combo.id,
        schemas.ComboUpdate(precio=Decimal("9.50"), producto_ids=[producto_a.id]),
        db=db,
    )
    updated_schema = schemas.Combo.model_validate(updated)
    assert updated_schema.precio == Decimal("9.50")
    assert [producto.id for producto in updated_schema.productos] == [producto_a.id]

    deleted = combos.delete_combo(combo.id, db=db)
    assert deleted.id == combo.id
    with pytest.raises(HTTPException) as exc_info:
        combos.read_combo(combo.id, db=db)
    assert exc_info.value.status_code == 404
