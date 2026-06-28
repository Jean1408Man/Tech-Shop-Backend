FROM python:3.11-slim

# Install uv using official binary copy
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install requirements via uv inside system site-packages for container simplicity
COPY pyproject.toml /code/pyproject.toml
RUN uv pip install --no-cache --system -r pyproject.toml

# Copy source code
COPY ./app /code/app

# Launch uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
