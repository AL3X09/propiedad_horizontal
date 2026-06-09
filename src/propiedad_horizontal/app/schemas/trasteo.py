from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class TrasteoBienCreate(BaseModel):
    """Schema para crear/actualizar bien en un trasteo"""
    bien_id: int = Field(..., gt=0)
    cantidad: int = Field(..., ge=1, description="Cantidad del bien")


class TrasteoBienRead(BaseModel):
    """Schema para leer bien en un trasteo"""
    id: int
    bien_id: int
    cantidad: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TrasteoBienDetail(TrasteoBienRead):
    """Schema extendido con detalles del bien"""
    bien_tipo: str = Field(default="", description="Tipo del bien")
    bien_descripcion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TrasteoCreate(BaseModel):
    """Schema para crear un trasteo"""
    usuario_id: int = Field(..., gt=0, description="ID del usuario propietario")
    fecha_ingreso: datetime = Field(..., description="Fecha de ingreso del trasteo")
    fecha_salida: Optional[datetime] = Field(default=None, description="Fecha de salida del trasteo")
    is_autorizado: bool = Field(default=False, description="¿Está autorizado el trasteo?")
    bienes: List[TrasteoBienCreate] = Field(..., min_length=1, description="Listado de bienes en el trasteo")


class TrasteoUpdate(BaseModel):
    """Schema para actualizar un trasteo"""
    usuario_id: Optional[int] = Field(default=None, gt=0)
    fecha_ingreso: Optional[datetime] = None
    fecha_salida: Optional[datetime] = None
    is_autorizado: Optional[bool] = None
    is_active: Optional[bool] = None
    bienes: Optional[List[TrasteoBienCreate]] = Field(default=None, description="Si se envía, reemplaza la lista completa de bienes")


class TrasteoRead(BaseModel):
    """Schema para leer trasteo sin detalles de bienes"""
    id: int
    usuario_id: int
    fecha_ingreso: datetime
    fecha_salida: Optional[datetime] = None
    is_autorizado: bool
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TrasteoReadDetail(TrasteoRead):
    """Schema extendido con detalles de bienes incluidos"""
    bienes: List[TrasteoBienDetail] = Field(default_factory=list, description="Bienes incluidos en el trasteo")

    model_config = ConfigDict(from_attributes=True)
