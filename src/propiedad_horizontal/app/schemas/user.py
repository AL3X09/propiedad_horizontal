from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from propiedad_horizontal.app.schemas.role import RoleRead

class UserCreate(BaseModel):
    username: str
    password: str
    role_id: Optional[int] = None

class UserUpdate(BaseModel):
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None
    must_change_password: Optional[bool] = None

class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool
    role: RoleRead
    must_change_password: bool
    password_changed_at: Optional[datetime] = None
    permissions: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    must_change_password: bool = False  # Indica si debe cambiar contraseña

class LoginRequest(BaseModel):
    username: str
    password: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    
class ForcePasswordChangeRequest(BaseModel):
    """Para cuando el usuario DEBE cambiar su contraseña"""
    new_password: str = Field(..., min_length=8)