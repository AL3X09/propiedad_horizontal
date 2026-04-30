from fastapi import APIRouter, Depends, HTTPException, Query
from propiedad_horizontal.app.schemas.vehicle_type import (
    VehicleTypeCreate,
    VehicleTypeUpdate,
    VehicleTypeRead,
    VehicleTypeToggle,
)
from propiedad_horizontal.app.services.vehicle_type_service import (
    create_vehicle_type,
    list_vehicle_types,
    get_vehicle_type,
    update_vehicle_type,
    toggle_vehicle_type,
    delete_vehicle_type,
    get_active_vehicle_types,
)
from propiedad_horizontal.app.core.auth import require_permissions


router = APIRouter(prefix="/parking/vehicle-types", tags=["vehicle-types"])


@router.get("/", response_model=list[VehicleTypeRead], dependencies=[Depends(require_permissions(["parking:read"]))])
async def list_vehicle_types_endpoint(
    include_inactive: bool = Query(False, description="Incluir tipos inactivos"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Lista todos los tipos de vehículos.
    Por defecto solo retorna los activos.
    """
    items = await list_vehicle_types(include_inactive=include_inactive, limit=limit, offset=offset)
    return [VehicleTypeRead.model_validate(vt) for vt in items]


@router.get("/active", response_model=list[VehicleTypeRead])
async def list_active_vehicle_types_endpoint():
    """
    Lista solo tipos de vehículos activos.
    Útil para selects en UI.
    """
    items = await get_active_vehicle_types()
    return [VehicleTypeRead.model_validate(vt) for vt in items]


@router.get("/{vt_id}", response_model=VehicleTypeRead, dependencies=[Depends(require_permissions(["parking:read"]))])
async def get_vehicle_type_endpoint(vt_id: int):
    vt = await get_vehicle_type(vt_id)
    if not vt:
        raise HTTPException(status_code=404, detail="Tipo de vehículo no encontrado")
    return VehicleTypeRead.model_validate(vt)


@router.post("/", response_model=VehicleTypeRead, status_code=201, dependencies=[Depends(require_permissions(["parking:write"]))])
async def create_vehicle_type_endpoint(payload: VehicleTypeCreate):
    try:
        vt = await create_vehicle_type(payload)
        return VehicleTypeRead.model_validate(vt)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{vt_id}", response_model=VehicleTypeRead, dependencies=[Depends(require_permissions(["parking:write"]))])
async def update_vehicle_type_endpoint(vt_id: int, payload: VehicleTypeUpdate):
    vt = await update_vehicle_type(vt_id, payload)
    if not vt:
        raise HTTPException(status_code=404, detail="Tipo de vehículo no encontrado")
    return VehicleTypeRead.model_validate(vt)


@router.post("/{vt_id}/toggle", response_model=VehicleTypeRead, dependencies=[Depends(require_permissions(["parking:write"]))])
async def toggle_vehicle_type_endpoint(vt_id: int, payload: VehicleTypeToggle):
    vt = await toggle_vehicle_type(vt_id, payload.is_active)
    if not vt:
        raise HTTPException(status_code=404, detail="Tipo de vehículo no encontrado")
    return VehicleTypeRead.model_validate(vt)


@router.delete("/{vt_id}", status_code=204, dependencies=[Depends(require_permissions(["parking:write"]))])
async def delete_vehicle_type_endpoint(vt_id: int):
    """
    Desactiva un tipo de vehículo (soft-delete).
    """
    ok = await delete_vehicle_type(vt_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tipo de vehículo no encontrado")
    return None
