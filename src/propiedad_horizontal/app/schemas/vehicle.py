from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class VehicleCreate(BaseModel):
    """Schema para crear un nuevo vehículo."""
    persona_id: int = Field(..., description="ID de la persona propietaria")
    vehicle_type_id: int = Field(..., description="ID del tipo de vehículo")
    placa_code: str = Field(..., max_length=20, description="Placa o código del vehículo")


class VehicleUpdate(BaseModel):
    """Schema para actualizar un vehículo."""
    persona_id: int | None = Field(None, description="ID de la persona propietaria")
    vehicle_type_id: int | None = Field(None, description="ID del tipo de vehículo")
    placa_code: str | None = Field(None, max_length=20, description="Placa o código")


class VehicleRead(BaseModel):
    """Schema de respuesta para vehículo."""
    id: int
    persona_id: int
    vehicle_type_id: int
    placa_code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VehicleToggle(BaseModel):
    """Schema para togglear estado activo/inactivo."""
    is_active: bool