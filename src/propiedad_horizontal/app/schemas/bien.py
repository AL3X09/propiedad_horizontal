from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BienCreate(BaseModel):
    tipo: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)


class BienUpdate(BaseModel):
    tipo: Optional[str] = Field(default=None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None


class BienToggle(BaseModel):
    is_active: bool


class BienRead(BaseModel):
    id: int
    tipo: str
    descripcion: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
