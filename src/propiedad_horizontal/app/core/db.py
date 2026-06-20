from contextlib import asynccontextmanager
from fastapi import FastAPI
from tortoise import Tortoise
from propiedad_horizontal.app.core.config import settings

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": settings.TORTOISE_MODELS,
            "default_connection": "default",
        }
    },
}

# Ya no se usa register_tortoise
async def init_tortoise():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)  # safe=True = no rompe tablas existentes

async def close_tortoise():
    await Tortoise.close_connections()
