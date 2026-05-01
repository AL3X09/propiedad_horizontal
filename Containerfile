FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    # Añadimos /app al path para que Python encuentre tus módulos
    PYTHONPATH=/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clonar el repositorio
RUN git clone https://github.com/AL3X09/propiedad_horizontal.git .

# Instalar poetry y dependencias
RUN pip install --no-cache-dir poetry
RUN poetry install --no-root --without dev

# IMPORTANTE: Instalar el proyecto actual en modo editable o como paquete
# Esto registra "propiedad_horizontal" en los site-packages de Python
RUN pip install -e .

RUN pip install --no-cache-dir asyncpg

EXPOSE 8001

# Ajustamos el CMD para asegurarnos de que llame al módulo correctamente
CMD ["python", "-m", "uvicorn", "propiedad_horizontal.app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2"]