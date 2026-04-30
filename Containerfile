FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git clone https://github.com/AL3X09/propiedad_horizontal.git .

# ❌ NUNCA hacer esto:
# COPY .env .env
# ENV JWT_SECRET_KEY=valor_real

RUN pip install --no-cache-dir pip --upgrade \
    && pip install --no-cache-dir "poetry-core>=2.0.0,<3.0.0" \
    && pip install --no-cache-dir . \
    && pip install --no-cache-dir asyncpg

EXPOSE 8001

CMD ["uvicorn", "propiedad_horizontal.app.main:app", \
     "--host", "0.0.0.0", "--port", "8001", "--workers", "2"]