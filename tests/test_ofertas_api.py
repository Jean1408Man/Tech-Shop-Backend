from decimal import Decimal

from tests.helpers import active_dates


def test_ofertas_crud_with_products(api_client, create_producto):
    producto_a = create_producto(nombre="Cafe", precio_base="10.00")
    producto_b = create_producto(nombre="Pan", precio_base="2.50")

    create_response = api_client.post(
        "/api/v1/ofertas/",
        json_body={
            **active_dates(),
            "nombre": "Oferta desayuno",
            "descripcion": "Descuento inicial",
            "monto_descuento": "1.50",
            "producto_ids": [producto_a["id"]],
        },
    )
    assert create_response.status_code == 201
    oferta = create_response.body
    assert oferta["nombre"] == "Oferta desayuno"
    assert [producto["id"] for producto in oferta["productos"]] == [producto_a["id"]]

    list_response = api_client.get("/api/v1/ofertas/")
    assert list_response.status_code == 200
    assert [oferta["id"] for oferta in list_response.body] == [oferta["id"]]

    get_response = api_client.get(f"/api/v1/ofertas/{oferta['id']}")
    assert get_response.status_code == 200
    assert get_response.body["id"] == oferta["id"]

    update_response = api_client.put(
        f"/api/v1/ofertas/{oferta['id']}",
        json_body={
            "nombre": "Oferta desayuno actualizada",
            "monto_descuento": "2.25",
            "producto_ids": [producto_a["id"], producto_b["id"]],
        },
    )
    assert update_response.status_code == 200
    updated = update_response.body
    assert updated["nombre"] == "Oferta desayuno actualizada"
    assert Decimal(updated["monto_descuento"]) == Decimal("2.25")
    assert {producto["id"] for producto in updated["productos"]} == {
        producto_a["id"],
        producto_b["id"],
    }

    delete_response = api_client.delete(f"/api/v1/ofertas/{oferta['id']}")
    assert delete_response.status_code == 200
    assert api_client.get(f"/api/v1/ofertas/{oferta['id']}").status_code == 404


def test_ofertas_validate_product_ids_and_return_products(api_client, create_producto):
    invalid_response = api_client.post(
        "/api/v1/ofertas/",
        json_body={
            **active_dates(),
            "nombre": "Oferta invalida",
            "descripcion": None,
            "monto_descuento": "3.00",
            "producto_ids": [999],
        },
    )
    assert invalid_response.status_code == 400

    producto = create_producto()
    valid_response = api_client.post(
        "/api/v1/ofertas/",
        json_body={
            **active_dates(),
            "nombre": "Oferta valida",
            "descripcion": "Con productos",
            "monto_descuento": "3.00",
            "producto_ids": [producto["id"]],
        },
    )
    assert valid_response.status_code == 201
    assert [producto["id"] for producto in valid_response.body["productos"]] == [
        producto["id"]
    ]
