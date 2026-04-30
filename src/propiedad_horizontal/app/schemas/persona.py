
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

class PersonaCreate(BaseModel):
    # CORRECCIÓN: Ahora se usa el ID del link (relación casa-torre) en lugar del ID de casa/apartamento
    casa_interior_link_id: int
    usuario_id: Optional[int] = None

    nombres: str = Field(min_length=1, max_length=120)
    apellidos: str = Field(min_length=1, max_length=120)
    edad: int = Field(ge=0, le=120)
    celular: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=150)

    is_propietario: bool = False
    is_arrendatario: bool = False
    acepta_terminosycondiciones: bool = False

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v is None:
            return v
        v = v.strip()
        if "@" not in v or "." not in v:
            raise ValueError("Correo parece inválido")
        return v

class PersonaUpdate(BaseModel):
    # CORRECCIÓN: Ahora se usa el ID del link en lugar del ID de casa/apartamento
    casa_interior_link_id: Optional[int] = None
    usuario_id: Optional[int] = None

    nombres: Optional[str] = Field(default=None, min_length=1, max_length=120)
    apellidos: Optional[str] = Field(default=None, min_length=1, max_length=120)
    edad: Optional[int] = Field(default=None, ge=0, le=120)
    celular: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=150)

    is_propietario: Optional[bool] = None
    is_arrendatario: Optional[bool] = None
    acepta_terminosycondiciones: Optional[bool] = None
    is_active: Optional[bool] = None

class PersonaRead(BaseModel):
    id: int
    # CORRECCIÓN: Ahora se usa el ID del link en lugar del ID de casa/apartamento
    casa_interior_link_id: int
    usuario_id: Optional[int]

    nombres: str
    apellidos: str
    edad: int
    celular: Optional[str]
    email: Optional[str]

    is_propietario: bool
    is_arrendatario: bool
    acepta_terminosycondiciones: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
