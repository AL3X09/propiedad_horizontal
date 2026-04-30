cat > /tmp/Containerfile.ph << 'EOF'
FROM python:3.11-slim

# Variables de build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Instalar dependencias del sistema + Poetry
RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# Clonar el repositorio
RUN git clone https://github.com/AL3X09/propiedad_horizontal.git .

# Instalar dependencias con Poetry (sin dev dependencies)
RUN poetry install --only main --no-root

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
EOF