from contextlib import asynccontextmanager
from fastapi import FastAPI
from tortoise import Tortoise
from propiedad_horizontal.app.core.config import settings

# Ya no se usa register_tortoise
async def init_tortoise():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)  # safe=True = no rompe tablas existentes

async def close_tortoise():
    await Tortoise.close_connections()


TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": [
                "propiedad_horizontal.app.models.user",
                "propiedad_horizontal.app.models.role",
                "propiedad_horizontal.app.models.permission",
                "propiedad_horizontal.app.models.parking",
                "propiedad_horizontal.app.models.parking_assignment",
                "propiedad_horizontal.app.models.parking_reservation",
                "propiedad_horizontal.app.models.propiedad_horizontal",
                "propiedad_horizontal.app.models.persona",
                "propiedad_horizontal.app.models.torre_interior",
                "propiedad_horizontal.app.models.casa_apartamento",
                "propiedad_horizontal.app.models.casa_apartamento_interior_torre",
                "propiedad_horizontal.app.models.parking_lottery_config",
                "propiedad_horizontal.app.models.parking_lottery_round",
                "propiedad_horizontal.app.models.parking_lottery_participant",
                "propiedad_horizontal.app.models.resident_behavior",
                "propiedad_horizontal.app.models.vehicle_type",
                "propiedad_horizontal.app.models.vehicle",
                "aerich.models",
            ],
            "default_connection": "default",
        }
    },
}