from pydantic import BaseModel, ConfigDict, Field

class VehicleTypeCreate(BaseModel):
    """Schema para crear un nuevo tipo de vehículo."""
    name: str = Field(max_length=100, description="Nombre para mostrar")
    emoji: str | None = Field(None, max_length=10, description="Emoji para UI")
    description: str | None = Field(None, max_length=255, description="Descripción opcional")
    display_order: int = Field(0, description="Orden de visualización")


class VehicleTypeUpdate(BaseModel):
    """Schema para actualizar un tipo de vehículo."""
    name: str | None = Field(None, max_length=100)
    emoji: str | None = Field(None, max_length=10)
    description: str | None = Field(None, max_length=255)
    display_order: int | None = Field(None)


class VehicleTypeRead(BaseModel):
    """Schema de respuesta para tipo de vehículo."""
    id: int
    name: str
    emoji: str | None
    description: str | None
    display_order: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class VehicleTypeToggle(BaseModel):
    """Schema para togglear estado activo/inactivo."""
    is_active: bool