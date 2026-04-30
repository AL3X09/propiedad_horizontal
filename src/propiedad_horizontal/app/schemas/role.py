from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from propiedad_horizontal.app.schemas.permission import PermissionRead


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)
    permissions: List[str] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)
    permissions: Optional[List[str]] = None


class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[PermissionRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
