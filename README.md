# Orbita Backend

FastAPI + MySQL containerized project backend.

## Requisitos
- [Docker](https://www.docker.com/) y Docker Compose
- [uv](https://github.com/astral-sh/uv) (opcional, para desarrollo local fuera de Docker)

## Comenzando

### 1. Iniciar los servicios con Docker
```bash
docker compose up -d --build
```

### 2. Generar y aplicar migraciones de base de datos (Alembic)
```bash
# Crear migración inicial
docker compose run --rm web alembic revision --autogenerate -m "Initial migration"

# Aplicar las migraciones
docker compose run --rm web alembic upgrade head
```

### 3. Verificar estado de la API
```bash
curl http://localhost:8000/health
```
Consulte la documentación interactiva en:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
