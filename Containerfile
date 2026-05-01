FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/tmp/poetry_cache'

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Instalar Poetry
RUN pip install --no-cache-dir poetry

# 2. Clonar el repositorio
RUN git clone https://github.com/AL3X09/propiedad_horizontal.git .

# 3. Instalar dependencias usando Poetry
# Nota: Esto instalará python-multipart si ya lo agregaste con 'poetry add'
RUN poetry install --no-root --without dev \
    && pip install --no-cache-dir asyncpg \
    && rm -rf $POETRY_CACHE_DIR

# Exponer el puerto
EXPOSE 8001

# Comando de ejecución
CMD ["uvicorn", "propiedad_horizontal.app.main:app", \
     "--host", "0.0.0.0", "--port", "8001", "--workers", "2"]