import os
import json
from pydantic_settings import BaseSettings
from pydantic import Field, AnyUrl
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = Field(default="FastAPI Monolito", description="Nombre de la app")
    DEBUG: bool = True

    DB_URL: str = "sqlite://db.sqlite3"

    TORTOISE_MODELS: List[str] = [
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
        # Nuevos modelos del sistema de lottery de parqueaderos
        "propiedad_horizontal.app.models.parking_lottery_config",
        "propiedad_horizontal.app.models.parking_lottery_round",
        "propiedad_horizontal.app.models.parking_lottery_participant",
        "propiedad_horizontal.app.models.resident_behavior",
        "propiedad_horizontal.app.models.vehicle_type",
        "propiedad_horizontal.app.models.vehicle",
    ]

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRES_MINUTES: int

    API_URL: AnyUrl = Field(
        default="http://localhost:8000",
        description="URL base de la API, usada para construir enlaces en emails y QR",
    )

    # CORS configuration
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="Orígenes permitidos para CORS (separar por comas en .env)"
    )

    # Notificaciones service configuration (obligatorias para producción)
    NOTIFICACIONES_SERVICE_URL: str = Field(
        ...,
        description="URL base del servicio de notificaciones (email/SMS)"
    )
    NOTIFICACIONES_API_KEY: str = Field(
        ...,
        description="API Key para autenticación con el servicio de notificaciones"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Timezone global para la aplicación (Bogotá, Colombia)
APP_TIMEZONE = "America/Bogota"

settings = Settings()
