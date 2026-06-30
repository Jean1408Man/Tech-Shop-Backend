from decimal import Decimal

from tests.helpers import active_dates


def _create_combo(api_client, producto_ids, precio: str = "11.00"):
    response = api_client.post(
        "/api/v1/combos/",
        json_body={
            "nombre": "Desayuno",
            "descripcion": "Cafe con pan",
            "precio": precio,
            "imagen": "https://example.com/combo.png",
            "producto_ids": producto_ids,
        },
    )
    assert response.status_code == 201
    return response.body


def _create_oferta(
    api_client,
    producto_ids,
    monto_descuento: str = "1.50",
    dates: dict[str, str] | None = None,
):
    response = api_client.post(
        "/api/v1/ofertas/",
        json_body={
            **(dates or active_dates()),
            "nombre": "Oferta pedido",
            "descripcion": "Descuento para pedido",
            "monto_descuento": monto_descuento,
            "imagen": "https://example.com/oferta.png",
            "producto_ids": producto_ids,
        },
    )
    assert response.status_code == 201
    return response.body


def test_pedidos_crud_with_products_combos_and_snapshots(api_client, create_producto):
    producto_a = create_producto(nombre="Cafe", precio_base="10.00")
    producto_b = create_producto(nombre="Pan", precio_base="2.50")
    oferta = _create_oferta(api_client, [producto_a["id"]], monto_descuento="1.50")
    combo = _create_combo(api_client, [producto_a["id"], producto_b["id"]])

    create_response = api_client.post(
        "/api/v1/pedidos/",
        json_body={
            "nombre": "Ana",
            "telefono": "055512345",
            "productos": [
                {
                    "producto_id": producto_a["id"],
                    "cantidad": 2,
                    "oferta_id": oferta["id"],
                }
            ],
            "combos": [{"combo_id": combo["id"], "cantidad": 1}],
        },
    )
    assert create_response.status_code == 201
    pedido = create_response.body
    assert pedido["nombre"] == "Ana"
    assert pedido["telefono"] == "055512345"
    assert pedido["fecha"]
    assert Decimal(pedido["total"]) == Decimal("28.00")

    producto_line = pedido["productos"][0]
    assert producto_line["producto_id"] == producto_a["id"]
    assert producto_line["oferta_id"] == oferta["id"]
    assert producto_line["cantidad"] == 2
    assert producto_line["producto_nombre"] == "Cafe"
    assert Decimal(producto_line["precio_unitario"]) == Decimal("10.00")
    assert producto_line["oferta_nombre"] == "Oferta pedido"
    assert Decimal(producto_line["descuento_unitario"]) == Decimal("1.50")
    assert Decimal(producto_line["subtotal"]) == Decimal("17.00")

    combo_line = pedido["combos"][0]
    assert combo_line["combo_id"] == combo["id"]
    assert combo_line["cantidad"] == 1
    assert combo_line["combo_nombre"] == "Desayuno"
    assert Decimal(combo_line["precio_unitario"]) == Decimal("11.00")
    assert Decimal(combo_line["subtotal"]) == Decimal("11.00")

    list_response = api_client.get("/api/v1/pedidos/")
    assert list_response.status_code == 200
    assert [pedido["id"] for pedido in list_response.body] == [pedido["id"]]

    get_response = api_client.get(f"/api/v1/pedidos/{pedido['id']}")
    assert get_response.status_code == 200
    assert get_response.body["id"] == pedido["id"]

    update_response = api_client.put(
        f"/api/v1/pedidos/{pedido['id']}",
        json_body={
            "nombre": "Ana actualizada",
            "combos": [{"combo_id": combo["id"], "cantidad": 2}],
        },
    )
    assert update_response.status_code == 200
    updated = update_response.body
    assert updated["nombre"] == "Ana actualizada"
    assert Decimal(updated["total"]) == Decimal("39.00")
    assert updated["productos"][0]["id"] == producto_line["id"]
    assert updated["combos"][0]["id"] != combo_line["id"]
    assert updated["combos"][0]["cantidad"] == 2

    delete_response = api_client.delete(f"/api/v1/pedidos/{pedido['id']}")
    assert delete_response.status_code == 200
    assert api_client.get(f"/api/v1/pedidos/{pedido['id']}").status_code == 404


def test_pedidos_auto_apply_current_offer(api_client, create_producto):
    producto = create_producto(nombre="Cafe", precio_base="10.00")
    oferta = _create_oferta(api_client, [producto["id"]], monto_descuento="2.00")

    response = api_client.post(
        "/api/v1/pedidos/",
        json_body={
            "nombre": "Ana",
            "telefono": "55512345",
            "productos": [{"producto_id": producto["id"], "cantidad": 1}],
        },
    )
    assert response.status_code == 201
    line = response.body["productos"][0]
    assert line["oferta_id"] == oferta["id"]
    assert Decimal(line["descuento_unitario"]) == Decimal("2.00")
    assert Decimal(line["subtotal"]) == Decimal("8.00")


def test_pedidos_validate_items_and_offers(api_client, create_producto):
    producto = create_producto(nombre="Cafe", precio_base="10.00")
    other_producto = create_producto(nombre="Pan", precio_base="2.50")
    oferta = _create_oferta(api_client, [other_producto["id"]])

    empty_response = api_client.post(
        "/api/v1/pedidos/",
        json_body={"nombre": "Ana", "telefono": "55512345"},
    )
    assert empty_response.status_code == 400
    assert empty_response.body["detail"] == (
        "El pedido debe tener al menos un producto o combo."
    )

    missing_product_response = api_client.post(
        "/api/v1/pedidos/",
        json_body={
            "nombre": "Ana",
            "telefono": "55512345",
            "productos": [{"producto_id": 999, "cantidad": 1}],
        },
    )
    assert missing_product_response.status_code == 400
    assert missing_product_response.body["detail"] == "Producto no encontrado."

    missing_combo_response = api_client.post(
        "/api/v1/pedidos/",
        json_body={
            "nombre": "Ana",
            "telefono": "55512345",
            "combos": [{"combo_id": 999, "cantidad": 1}],
        },
    )
    assert missing_combo_response.status_code == 400
    assert missing_combo_response.body["detail"] == "Combo no encontrado."

    wrong_offer_response = api_client.post(
        "/api/v1/pedidos/",
        json_body={
            "nombre": "Ana",
            "telefono": "55512345",
            "productos": [
                {
                    "producto_id": producto["id"],
                    "cantidad": 1,
                    "oferta_id": oferta["id"],
                }
            ],
        },
    )
    assert wrong_offer_response.status_code == 400
    assert wrong_offer_response.body["detail"] == (
        "La oferta no pertenece al producto indicado."
    )


def test_pedidos_reject_inactive_offer(api_client, create_producto):
    producto = create_producto(nombre="Cafe", precio_base="10.00")
    future_dates = active_dates()
    future_dates["fecha_inicio"] = "2999-01-01T00:00:00+00:00"
    future_dates["fecha_fin"] = "2999-01-02T00:00:00+00:00"
    oferta = _create_oferta(api_client, [producto["id"]], dates=future_dates)

    response = api_client.post(
        "/api/v1/pedidos/",
        json_body={
            "nombre": "Ana",
            "telefono": "55512345",
            "productos": [
                {
                    "producto_id": producto["id"],
                    "cantidad": 1,
                    "oferta_id": oferta["id"],
                }
            ],
        },
    )
    assert response.status_code == 400
    assert response.body["detail"] == "La oferta no esta activa para la fecha del pedido."
