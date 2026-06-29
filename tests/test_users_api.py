def _login(api_client, email: str, password: str = "secret123") -> str:
    response = api_client.post(
        "/api/v1/auth/login",
        form={"username": email, "password": password},
    )
    assert response.status_code == 200
    return response.body["access_token"]


def test_users_endpoints_read_update_and_delete(api_client, create_user):
    current_user = create_user(email="current@example.com", full_name="Actual")
    other_user = create_user(email="other@example.com", full_name="Otro")
    token = _login(api_client, "current@example.com")

    me_response = api_client.get("/api/v1/users/me", token=token)
    assert me_response.status_code == 200
    assert me_response.body["id"] == current_user["id"]

    update_me_response = api_client.put(
        "/api/v1/users/me",
        json_body={"full_name": "Actualizada"},
        token=token,
    )
    assert update_me_response.status_code == 200
    assert update_me_response.body["full_name"] == "Actualizada"

    list_response = api_client.get("/api/v1/users/", token=token)
    assert list_response.status_code == 200
    assert {user["email"] for user in list_response.body} == {
        "current@example.com",
        "other@example.com",
    }

    get_response = api_client.get(f"/api/v1/users/{other_user['id']}", token=token)
    assert get_response.status_code == 200
    assert get_response.body["email"] == "other@example.com"

    assert api_client.get("/api/v1/users/999", token=token).status_code == 404

    delete_response = api_client.delete(f"/api/v1/users/{other_user['id']}", token=token)
    assert delete_response.status_code == 200
    assert (
        api_client.delete(f"/api/v1/users/{other_user['id']}", token=token).status_code
        == 404
    )
