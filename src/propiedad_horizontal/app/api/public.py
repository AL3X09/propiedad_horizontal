from fastapi import APIRouter
from typing import List

from propiedad_horizontal.app.models.vehicle_type import VehicleType
from propiedad_horizontal.app.models.casa_apartamento_interior_torre import CasaApartamentoInteriorTorre
from propiedad_horizontal.app.schemas.vehicle_type import VehicleTypeRead

#API PUBLICA PARA CONSULTAR EN EL FORMULARIO PUBLICO DE RESERVAS

router = APIRouter(prefix="/public", tags=["public"])

# ---- ENDPOINTS PÚBLICOS (SIN AUTH) ----
@router.get("/vehicle-types", tags=["public"], response_model=List[VehicleTypeRead])
async def list_vehicle_types():
    """Lista tipos de vehículo activos para el formulario público."""
    return await VehicleType.filter(is_active=True).order_by("display_order").all()

@router.get("/interior-links", tags=["public"], response_model=List[dict])
async def list_locations():
    """Lista ubicaciones disponibles para el formulario público."""
    locations = await CasaApartamentoInteriorTorre.all().prefetch_related("casa_apartamento", "torre_interior")
    return [
        {
            "id": l.id,
            "torre": l.torre_interior.t_numero_letra if l.torre_interior else "",
            "apartamento": l.casa_apartamento.c_numero_letra if l.casa_apartamento else ""
        }
        for l in locations
    ]