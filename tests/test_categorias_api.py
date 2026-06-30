def test_categorias_crud(api_client):
    create_response = api_client.post(
        "/api/v1/categorias/",
        json_body={
            "nombre": "Bebidas",
            "descripcion": "Bebidas frias y calientes",
            "url_img": "https://example.com/bebidas.png",
        },
    )
    assert create_response.status_code == 201
    categoria = create_response.body
    assert categoria["nombre"] == "Bebidas"
    assert categoria["url_img"] == "https://example.com/bebidas.png"
    assert categoria["productos"] == []

    list_response = api_client.get("/api/v1/categorias/")
    assert list_response.status_code == 200
    assert [categoria["id"] for categoria in list_response.body] == [categoria["id"]]

    get_response = api_client.get(f"/api/v1/categorias/{categoria['id']}")
    assert get_response.status_code == 200
    assert get_response.body["id"] == categoria["id"]

    update_response = api_client.put(
        f"/api/v1/categorias/{categoria['id']}",
        json_body={"nombre": "Bebidas premium"},
    )
    assert update_response.status_code == 200
    assert update_response.body["nombre"] == "Bebidas premium"

    delete_response = api_client.delete(f"/api/v1/categorias/{categoria['id']}")
    assert delete_response.status_code == 200
    assert api_client.get(f"/api/v1/categorias/{categoria['id']}").status_code == 404


def test_categoria_returns_products_and_cannot_delete_with_products(
    api_client,
    create_categoria,
    create_producto,
):
    categoria = create_categoria(nombre="Panaderia")
    producto = create_producto(
        nombre="Pan",
        precio_base="2.50",
        categoria_id=categoria["id"],
    )

    get_response = api_client.get(f"/api/v1/categorias/{categoria['id']}")
    assert get_response.status_code == 200
    assert [producto["id"] for producto in get_response.body["productos"]] == [
        producto["id"]
    ]

    delete_response = api_client.delete(f"/api/v1/categorias/{categoria['id']}")
    assert delete_response.status_code == 400
    assert (
        delete_response.body["detail"]
        == "No se puede eliminar una categoria con productos asociados."
    )
