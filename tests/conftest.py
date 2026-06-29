import json
import socket
import threading
import time
from dataclasses import dataclass
from typing import Any, Optional
from urllib import error, parse, request

import pytest
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.core.database import Base, get_db
from app.main import app


@dataclass
class ApiResponse:
    status_code: int
    body: Any
    text: str


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get(self, path: str, token: Optional[str] = None) -> ApiResponse:
        return self.request("GET", path, token=token)

    def post(
        self,
        path: str,
        json_body: Any = None,
        form: Optional[dict[str, Any]] = None,
        token: Optional[str] = None,
    ) -> ApiResponse:
        return self.request("POST", path, json_body=json_body, form=form, token=token)

    def put(
        self,
        path: str,
        json_body: Any = None,
        token: Optional[str] = None,
    ) -> ApiResponse:
        return self.request("PUT", path, json_body=json_body, token=token)

    def delete(self, path: str, token: Optional[str] = None) -> ApiResponse:
        return self.request("DELETE", path, token=token)

    def request(
        self,
        method: str,
        path: str,
        json_body: Any = None,
        form: Optional[dict[str, Any]] = None,
        token: Optional[str] = None,
    ) -> ApiResponse:
        headers = {"Accept": "application/json"}
        data = None

        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif form is not None:
            data = parse.urlencode(form).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        if token:
            headers["Authorization"] = f"Bearer {token}"

        req = request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with request.urlopen(req, timeout=10) as response:
                text = response.read().decode("utf-8")
                return ApiResponse(response.status, _parse_json(text), text)
        except error.HTTPError as exc:
            text = exc.read().decode("utf-8")
            return ApiResponse(exc.code, _parse_json(text), text)


def _parse_json(text: str) -> Any:
    if not text:
        return None
    return json.loads(text)


@pytest.fixture()
def api_client():
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

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    port = _free_port()
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    _wait_for_server(server)

    yield ApiClient(f"http://127.0.0.1:{port}")

    server.should_exit = True
    thread.join(timeout=5)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_server(server: uvicorn.Server) -> None:
    deadline = time.time() + 10
    while time.time() < deadline:
        if server.started:
            return
        time.sleep(0.05)
    raise RuntimeError("Uvicorn test server did not start.")


@pytest.fixture()
def create_producto(api_client):
    def _create_producto(nombre: str = "Cafe", precio_base: str = "10.50"):
        response = api_client.post(
            "/api/v1/productos/",
            json_body={
                "nombre": nombre,
                "descripcion": "Producto de prueba",
                "precio_base": precio_base,
                "url_img": "https://example.com/producto.png",
            },
        )
        assert response.status_code == 201
        return response.body

    return _create_producto


@pytest.fixture()
def create_user(api_client):
    def _create_user(
        email: str = "ana@example.com",
        password: str = "secret123",
        full_name: str = "Ana",
    ):
        response = api_client.post(
            "/api/v1/auth/register",
            json_body={
                "email": email,
                "password": password,
                "full_name": full_name,
                "is_active": True,
            },
        )
        assert response.status_code == 201
        return response.body

    return _create_user
