from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class PermissionCreate(BaseModel):
    code: str = Field(min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)

class PermissionUpdate(BaseModel):
    code: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)

class PermissionRead(BaseModel):
    id: int
    code: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)