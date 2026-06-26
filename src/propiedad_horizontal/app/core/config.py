from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional



class Settings(BaseSettings):
    # ============================================================
    # APLICACIÓN
    # ============================================================
    APP_NAME: str = Field(...)
    APP_HOST: str = Field(...)
    APP_PORT: int = Field(...)
    ENVIRONMENT: str = Field(...)
    APP_VERSION: str = "1.0.9"
    APP_DESCRIPTION: str = "API para gestión de propiedad horizontal"
    APP_CONTACT_NAME: str = "Soporte Técnico"
    APP_CONTACT_EMAIL: str = "soporte@propiedadhorizontal.com"
    APP_TERMS_OF_SERVICE: str = "https://propiedadhorizontal.com/terminos"
    APP_LICENSE: str = "Propietario"

    # ============================================================
    # BASE DE DATOS
    # ============================================================
    DATABASE_URL: str = Field(...)

    # Opcionales: solo requeridos cuando el engine es postgres/mysql
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None

    @model_validator(mode="after")
    def validate_db_fields(self) -> "Settings":
        """
        Si DATABASE_URL es de postgres o mysql, exige los campos DB_*.
        Si es sqlite, los ignora completamente.
        """
        url = self.DATABASE_URL.lower()
        if url.startswith("sqlite"):
            return self  # nada que validar

        missing = [
            field
            for field, val in {
                "DB_HOST": self.DB_HOST,
                "DB_PORT": self.DB_PORT,
                "DB_NAME": self.DB_NAME,
                "DB_USER": self.DB_USER,
                "DB_PASSWORD": self.DB_PASSWORD,
            }.items()
            if val is None
        ]
        if missing:
            raise ValueError(
                f"Los siguientes campos son requeridos cuando DATABASE_URL "
                f"no es sqlite: {', '.join(missing)}"
            )
        return self

    # ============================================================
    # Tortoise ORM
    # ============================================================
    TORTOISE_MODELS: List[str] = [
        "propiedad_horizontal.app.models.user",
                "propiedad_horizontal.app.models.role",
                "propiedad_horizontal.app.models.permission",
                "propiedad_horizontal.app.models.bien",
                "propiedad_horizontal.app.models.trasteo",
                "propiedad_horizontal.app.models.trasteo_bien",
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
                "propiedad_horizontal.app.models.domain_config",
                "aerich.models",
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
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # ← ignora DB_ENGINE y cualquier extra del .env
    )


# Timezone global para la aplicación (Bogotá, Colombia)
APP_TIMEZONE = "America/Bogota"

settings = Settings()