from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional

class PropiedadHorizontalCreate(BaseModel):
    nombre: str
    direccion: str
    telefono: Optional[str] = None
    localidad: Optional[str] = None
    barrio: Optional[str] = None
    correo: Optional[str] = None

    # Validaciones ligeras
    @field_validator("telefono")
    @classmethod
    def validate_telefono(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) > 20:
            raise ValueError("Teléfono demasiado largo (máx 20)")
        return v

    @field_validator("correo")
    @classmethod
    def validate_correo(cls, v):
        if v is None:
            return v
        v = v.strip()
        # Validación simple (no estricta); si quieres EmailStr, te lo configuro
        if "@" not in v or "." not in v:
            raise ValueError("Correo parece inválido")
        return v

class PropiedadHorizontalUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    localidad: Optional[str] = None
    barrio: Optional[str] = None
    correo: Optional[str] = None

class PropiedadHorizontalRead(BaseModel):
    id: int
    nombre: str
    direccion: str
    telefono: Optional[str]
    localidad: Optional[str]
    barrio: Optional[str]
    correo: Optional[str]

    model_config = ConfigDict(from_attributes=True)
