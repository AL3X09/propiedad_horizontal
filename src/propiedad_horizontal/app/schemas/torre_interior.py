from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class TorreInteriorCreate(BaseModel):
    t_numero_letra: str = Field(min_length=1, max_length=20)

class TorreInteriorUpdate(BaseModel):
    t_numero_letra: Optional[str] = Field(default=None, min_length=1, max_length=20)
    is_active: Optional[bool] = None

class TorreInteriorRead(BaseModel):
    id: int
    t_numero_letra: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
