# Orbita Backend

FastAPI + MySQL containerized project backend.

## Requisitos
- [Docker](https://www.docker.com/) y Docker Compose
- [uv](https://github.com/astral-sh/uv) (opcional, para desarrollo local fuera de Docker)

## Comenzando

### 1. Crear archivo de entorno
```bash
cp .env.example .env
```

Si vas a levantar la API con Docker Compose, asegúrate de que en `.env` quede:

```env
MYSQL_HOST=db
```

Si vas a ejecutar la API localmente fuera de Docker y solo la base de datos está en Docker, usa:

```env
MYSQL_HOST=localhost
```

### 2. Iniciar los servicios con Docker
```bash
docker compose up -d --build
```

### 3. Aplicar migraciones de base de datos (Alembic)
```bash
docker compose run --rm web alembic upgrade head
```

### 4. Verificar estado de la API
```bash
curl http://localhost:8000/health
```

Consulte la documentación interactiva en:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Probar endpoints manualmente

### Crear usuario
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ana@example.com",
    "password": "secret123",
    "full_name": "Ana"
  }'
```

### Login y token
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ana@example.com&password=secret123" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

### Consultar usuario autenticado
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Crear categoria
```bash
curl -X POST http://localhost:8000/api/v1/categorias/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Bebidas",
    "descripcion": "Bebidas frias y calientes",
    "url_img": "https://example.com/bebidas.png"
  }'
```

### Crear producto
```bash
curl -X POST http://localhost:8000/api/v1/productos/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Cafe",
    "descripcion": "Cafe molido",
    "precio_base": "10.50",
    "url_img": "https://example.com/cafe.png",
    "categoria_id": 1
  }'
```

### Crear oferta asociada a productos
```bash
curl -X POST http://localhost:8000/api/v1/ofertas/ \
  -H "Content-Type: application/json" \
  -d '{
    "fecha_inicio": "2026-06-29T00:00:00",
    "fecha_fin": "2026-07-29T23:59:59",
    "nombre": "Oferta de verano",
    "descripcion": "Descuento temporal",
    "monto_descuento": "2.00",
    "producto_ids": [1]
  }'
```

### Crear combo asociado a productos
```bash
curl -X POST http://localhost:8000/api/v1/combos/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Desayuno",
    "descripcion": "Cafe con pan",
    "precio": "11.00",
    "producto_ids": [1]
  }'
```

## Ejecutar tests

Los tests están organizados por dominio dentro de `tests/` y hacen peticiones HTTP reales contra una instancia temporal de Uvicorn usando SQLite en memoria.

```bash
.venv/bin/python -m pytest tests -q
```

Si el entorno restringe sockets locales, habilita permisos para ejecutar el servidor temporal de pruebas.
