from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from propiedad_horizontal.app.domain.enums import ApartmentStatus
from propiedad_horizontal.app.schemas.casa_apartamento import CasaApartamentoRead
from propiedad_horizontal.app.schemas.torre_interior import TorreInteriorRead

class CasaInteriorLinkCreate(BaseModel):
    casa_apartamento_id: int
    torre_interior_id: int
    status: ApartmentStatus = ApartmentStatus.DESHABITADO
    num_habitaciones: Optional[int] = Field(default=None, ge=0)

class CasaInteriorLinkUpdate(BaseModel):
    status: Optional[ApartmentStatus] = None
    num_habitaciones: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None

class CasaInteriorLinkRead(BaseModel):
    id: int
    casa_apartamento_id: int
    torre_interior_id: int
    status: ApartmentStatus
    num_habitaciones: Optional[int]
    is_active: bool
    casa_apartamento: Optional[CasaApartamentoRead] = None
    torre_interior: Optional[TorreInteriorRead] = None

    model_config = ConfigDict(from_attributes=True)
