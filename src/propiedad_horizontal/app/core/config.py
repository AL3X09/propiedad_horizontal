from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # ============================================================
    # APLICACIÓN
    # ============================================================
    APP_NAME: str = Field(...)
    APP_HOST: str = Field(...)
    APP_PORT: int = Field(...)
    ENVIRONMENT: str = Field(...)

    # ============================================================
    # BASE DE DATOS
    # ============================================================
    DATABASE_URL: str = Field(...)

    DB_HOST: str = Field(...)
    DB_PORT: int = Field(...)
    DB_NAME: str = Field(...)
    DB_USER: str = Field(...)
    DB_PASSWORD: str = Field(...)
    
    
    # ============================================================
    # Tortoise ORM
    # ============================================================
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
        "propiedad_horizontal.app.models.resident_behavior",
        "propiedad_horizontal.app.models.vehicle_type",
        "propiedad_horizontal.app.models.vehicle",
        # Nuevos modelos del sistema de lottery de parqueaderos
        "propiedad_horizontal.app.models.parking_lottery_config",
        "propiedad_horizontal.app.models.parking_lottery_round",
        "propiedad_horizontal.app.models.parking_lottery_participant",
    ]

    # ============================================================
    # SEGURIDAD / JWT
    # ============================================================
    JWT_SECRET_KEY: str = Field(...)
    JWT_ALGORITHM: str = Field(...)
    JWT_EXPIRES_MINUTES: int = Field(...)

    # ============================================================
    # SERVICIO DE NOTIFICACIONES
    # ============================================================
    NOTIFICACIONES_SERVICE_URL: str = Field(...)
    NOTIFICACIONES_API_KEY: str = Field(...)

    # ============================================================
    # CORS
    # ============================================================
    CORS_ORIGINS: List[str] = Field(...)

    # ============================================================
    # CONFIGURACIÓN PYDANTIC
    # ============================================================
    model_config = SettingsConfigDict(
        env_file=".env",       # ← se fuerza el archivo
        env_file_encoding="utf-8"
    )

# Timezone global para la aplicación (Bogotá, Colombia)
APP_TIMEZONE = "America/Bogota"

settings = Settings()