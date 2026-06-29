from decimal import Decimal
from time import sleep

from tests.helpers import active_dates


def test_productos_crud(api_client, create_producto):
    created = create_producto()
    assert created["nombre"] == "Cafe"
    assert Decimal(created["precio_base"]) == Decimal("10.50")
    assert created["oferta_actual"] is None

    list_response = api_client.get("/api/v1/productos/")
    assert list_response.status_code == 200
    assert [producto["id"] for producto in list_response.body] == [created["id"]]

    update_response = api_client.put(
        f"/api/v1/productos/{created['id']}",
        json_body={"nombre": "Cafe premium", "precio_base": "12.00"},
    )
    assert update_response.status_code == 200
    updated = update_response.body
    assert updated["nombre"] == "Cafe premium"
    assert Decimal(updated["precio_base"]) == Decimal("12.00")

    delete_response = api_client.delete(f"/api/v1/productos/{created['id']}")
    assert delete_response.status_code == 200
    assert api_client.get(f"/api/v1/productos/{created['id']}").status_code == 404


def test_producto_uses_latest_active_offer_by_creation_timestamp(
    api_client,
    create_producto,
):
    producto = create_producto()

    first_offer_response = api_client.post(
        "/api/v1/ofertas/",
        json_body={
            **active_dates(),
            "nombre": "Oferta vigente vieja",
            "descripcion": "Primera oferta vigente",
            "monto_descuento": "1.00",
            "producto_ids": [producto["id"]],
        },
    )
    assert first_offer_response.status_code == 201

    sleep(0.001)
    second_offer_response = api_client.post(
        "/api/v1/ofertas/",
        json_body={
            **active_dates(),
            "nombre": "Oferta vigente nueva",
            "descripcion": "Segunda oferta vigente",
            "monto_descuento": "2.00",
            "producto_ids": [producto["id"]],
        },
    )
    assert second_offer_response.status_code == 201

    future_dates = active_dates()
    future_dates["fecha_inicio"] = "2999-01-01T00:00:00+00:00"
    future_dates["fecha_fin"] = "2999-01-02T00:00:00+00:00"
    future_offer_response = api_client.post(
        "/api/v1/ofertas/",
        json_body={
            **future_dates,
            "nombre": "Oferta futura",
            "descripcion": "No debe aplicar todavia",
            "monto_descuento": "9.00",
            "producto_ids": [producto["id"]],
        },
    )
    assert future_offer_response.status_code == 201

    first_offer = first_offer_response.body
    second_offer = second_offer_response.body
    assert second_offer["fecha_creacion"] > first_offer["fecha_creacion"]
    assert "." in second_offer["fecha_creacion"]

    get_response = api_client.get(f"/api/v1/productos/{producto['id']}")
    assert get_response.status_code == 200
    oferta_actual = get_response.body["oferta_actual"]
    assert oferta_actual["nombre"] == "Oferta vigente nueva"
    assert Decimal(oferta_actual["monto_descuento"]) == Decimal("2.00")
