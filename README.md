##

# Crea el proyecto base
poetry new propiedad_horizontal
cd propiedad_horizontal

# Activa el entorno
source entornov/bin/activate
poetry shell

# Añade dependencias principales
poetry add fastapi uvicorn tortoise-orm pydantic-settings python-dotenv

# Migraciones con Aerich (como dev-dep)
poetry add -D aerich

# Tests
poetry add -D pytest pytest-asyncio httpx
poetry run pytest -q

##
Ejecutar
poetry install
Levanta el servidor (nota el módulo con layout src):
poetry run uvicorn propiedad_horizontal.app.main:app --reload
Abre: http://127.0.0.1:8000/docs
##
11) Migraciones con Aerich

# Inicializa Aerich (apunta al dict exportado)
poetry run aerich init -t propiedad_horizontal.app.core.db.TORTOISE_ORM

# Crea el esquema inicial
poetry run aerich init-db

# Después de cambios en modelos:
poetry run aerich migrate --name "add_fields_in_parking_reservation"

## Parking reservation QR workflow

### Regenerar o crear nuevo código QR

Si por algún motivo necesita generar un nuevo QR para una reserva existente (por ejemplo
el visitante perdió el anterior), puede ejecutar `python` con el siguiente snippet:

```python
from propiedad_horizontal.app.models.parking_reservation import VisitorReservation
from propiedad_horizontal.app.services.parking_reservation_service import _populate_qr

r = await VisitorReservation.get(id=123)
await _populate_qr(r)  # sustituye el token y actualiza qr_generated_at
```

Luego puede invocar `send_reservation_qr(r)` o ejecutar la lógica de envío de correo manualmente.
Este comportamiento está descrito en `app/services/parking_reservation_service.py`.

## Parking reservation QR workflow

1. When a visitor reservation is created, the system generates a unique `qr_token` and
   a PNG QR code is sent to the visitor's email (background task). The token is stored
   in `parking_visitor_reservations.qr_token`.
2. A GET request to `/parking/reservations/{id}/scan?token=<token>` represents a QR scan.
   * If the reservation is `ACTIVE` the status becomes `COMPLETED` and `updated_at` is updated.
   * If the reservation is already `COMPLETED`, the status becomes `FINISHED`, `ends_at` is set
     to now and `total_price` is calculated from `billed_minutes` × spot `minute_price`.
   * Any other state or invalid token returns HTTP 400/404.
3. Migrations include adding `qr_token` and `qr_generated_at` fields (see `migrations/models/1_...`).

The code is located in `app/services/parking_reservation_service.py` and helper modules
`app/utils/qr.py` + `app/utils/email.py`. Ensure `qrcode` and `fastapi-mail` are added to
`pyproject.toml` before installing.

poetry run aerich upgrade
#
El error ocurre porque SQLite no soporta ciertos cambios en columnas. La solución más segura es:

En desarrollo: Elimina la base de datos y recrea todo.
En producción: Usa una base de datos que soporte alteraciones (PostgreSQL, MySQL).

# Elimina la base de datos
rm db.sqlite3

# Elimina las migraciones existentes
rm -rf migrations/

# Inicia Aerich (creará la base de datos y las migraciones desde cero)
poetry run aerich init-db
# Después de cambios en modelos:
propiedad_horizontal/
├── README.md
├── poetry.lock
├── pyproject.toml
├── .env
├── src/
│   └── propiedad_horizontal/
│       ├── __init__.py
│       ├── app/
│       │   ├── core/
│       │   │   ├── config.py
│       │   │   └── db.py
│       │   ├── models/
│       │   │   └── user.py
│       │   ├── schemas/
│       │   │   └── user.py
│       │   ├── services/
│       │   │   └── user_service.py
│       │   ├── api/
│       │   │   └── routes.py
│       │   └── main.py
└── tests/
    ├── __init__.py
    └── test_users.py