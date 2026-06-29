def test_root_and_health_endpoints(api_client):
    root_response = api_client.get("/")
    assert root_response.status_code == 200
    assert root_response.body["message"].startswith("Welcome to the")

    health_response = api_client.get("/health")
    assert health_response.status_code == 200
    assert health_response.body["status"] == "healthy"
    assert health_response.body["database"] == "connected"
