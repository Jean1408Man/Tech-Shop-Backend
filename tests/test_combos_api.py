from decimal import Decimal


def test_combos_crud_with_products(api_client, create_producto):
    producto_a = create_producto(nombre="Cafe", precio_base="10.00")
    producto_b = create_producto(nombre="Pan", precio_base="2.50")

    create_response = api_client.post(
        "/api/v1/combos/",
        json_body={
            "nombre": "Desayuno",
            "descripcion": "Cafe con pan",
            "precio": "11.00",
            "imagen": "https://example.com/combo.png",
            "producto_ids": [producto_a["id"], producto_b["id"]],
        },
    )
    assert create_response.status_code == 201
    combo = create_response.body
    assert combo["nombre"] == "Desayuno"
    assert combo["imagen"] == "https://example.com/combo.png"
    assert {producto["id"] for producto in combo["productos"]} == {
        producto_a["id"],
        producto_b["id"],
    }

    list_response = api_client.get("/api/v1/combos/")
    assert list_response.status_code == 200
    assert [combo["id"] for combo in list_response.body] == [combo["id"]]

    get_response = api_client.get(f"/api/v1/combos/{combo['id']}")
    assert get_response.status_code == 200
    assert get_response.body["id"] == combo["id"]

    update_response = api_client.put(
        f"/api/v1/combos/{combo['id']}",
        json_body={
            "precio": "9.50",
            "imagen": "https://example.com/combo-actualizado.png",
            "producto_ids": [producto_a["id"]],
        },
    )
    assert update_response.status_code == 200
    updated = update_response.body
    assert Decimal(updated["precio"]) == Decimal("9.50")
    assert updated["imagen"] == "https://example.com/combo-actualizado.png"
    assert [producto["id"] for producto in updated["productos"]] == [producto_a["id"]]

    delete_response = api_client.delete(f"/api/v1/combos/{combo['id']}")
    assert delete_response.status_code == 200
    assert api_client.get(f"/api/v1/combos/{combo['id']}").status_code == 404
