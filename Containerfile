cat > /tmp/Containerfile.ph << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Clonar el repo dentro del contenedor durante el build
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/AL3X09/propiedad_horizontal.git .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
EOF

podman build -t propiedad-horizontal:latest -f /tmp/Containerfile.ph .