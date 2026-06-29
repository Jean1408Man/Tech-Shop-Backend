def test_auth_register_and_login_endpoints(api_client, create_user):
    user = create_user()
    assert user["email"] == "ana@example.com"
    assert user["full_name"] == "Ana"

    duplicate_response = api_client.post(
        "/api/v1/auth/register",
        json_body={
            "email": "ana@example.com",
            "password": "secret123",
            "full_name": "Ana",
        },
    )
    assert duplicate_response.status_code == 400

    token_response = api_client.post(
        "/api/v1/auth/login",
        form={"username": "ana@example.com", "password": "secret123"},
    )
    assert token_response.status_code == 200
    assert token_response.body["token_type"] == "bearer"
    assert token_response.body["access_token"]

    bad_login_response = api_client.post(
        "/api/v1/auth/login",
        form={"username": "ana@example.com", "password": "bad"},
    )
    assert bad_login_response.status_code == 400
