def test_items_endpoints_create_and_list(api_client):
    create_response = api_client.post(
        "/api/v1/items/",
        json_body={"title": "Primer item", "description": "Descripcion"},
    )
    assert create_response.status_code == 201
    created = create_response.body
    assert created["title"] == "Primer item"
    assert created["description"] == "Descripcion"

    list_response = api_client.get("/api/v1/items/")
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.body] == [created["id"]]
