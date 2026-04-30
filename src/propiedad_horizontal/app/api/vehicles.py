from fastapi import APIRouter, Depends, HTTPException, Query
from propiedad_horizontal.app.schemas.vehicle import (
    VehicleCreate,
    VehicleUpdate,
    VehicleRead,
    VehicleToggle,
)
from propiedad_horizontal.app.services.vehicle_service import (
    create_vehicle,
    list_vehicles,
    get_vehicle,
    update_vehicle,
    toggle_vehicle,
    delete_vehicle,
    get_active_vehicles,
)
from propiedad_horizontal.app.core.auth import require_permissions


router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/", response_model=list[VehicleRead], dependencies=[Depends(require_permissions(["parking:read"]))])
async def list_vehicles_endpoint(
    persona_id: int | None = Query(None, description="Filtrar por persona"),
    vehicle_type_id: int | None = Query(None, description="Filtrar por tipo de vehículo"),
    include_inactive: bool = Query(False, description="Incluir vehículos inactivos"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Lista todos los vehículos.
    Por defecto solo retorna los activos.
    """
    items = await list_vehicles(
        persona_id=persona_id,
        vehicle_type_id=vehicle_type_id,
        include_inactive=include_inactive,
        limit=limit,
        offset=offset,
    )
    return [VehicleRead.model_validate(v) for v in items]


@router.get("/active", response_model=list[VehicleRead])
async def list_active_vehicles_endpoint():
    """
    Lista solo vehículos activos.
    Útil para selects en UI.
    """
    items = await get_active_vehicles()
    return [VehicleRead.model_validate(v) for v in items]


@router.get("/{vehicle_id}", response_model=VehicleRead, dependencies=[Depends(require_permissions(["parking:read"]))])
async def get_vehicle_endpoint(vehicle_id: int):
    vehicle = await get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return VehicleRead.model_validate(vehicle)


@router.post("/", response_model=VehicleRead, status_code=201, dependencies=[Depends(require_permissions(["parking:write"]))])
async def create_vehicle_endpoint(payload: VehicleCreate):
    """
    Crea un nuevo vehículo.
    La placa debe ser única.
    """
    try:
        vehicle = await create_vehicle(payload)
        return VehicleRead.model_validate(vehicle)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{vehicle_id}", response_model=VehicleRead, dependencies=[Depends(require_permissions(["parking:write"]))])
async def update_vehicle_endpoint(vehicle_id: int, payload: VehicleUpdate):
    """
    Actualiza un vehículo existente.
    """
    try:
        vehicle = await update_vehicle(vehicle_id, payload)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")
        return VehicleRead.model_validate(vehicle)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{vehicle_id}/toggle", response_model=VehicleRead, dependencies=[Depends(require_permissions(["parking:write"]))])
async def toggle_vehicle_endpoint(vehicle_id: int, payload: VehicleToggle):
    """
    Activa o desactiva un vehículo.
    """
    vehicle = await toggle_vehicle(vehicle_id, payload.is_active)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return VehicleRead.model_validate(vehicle)


@router.delete("/{vehicle_id}", status_code=204, dependencies=[Depends(require_permissions(["parking:write"]))])
async def delete_vehicle_endpoint(vehicle_id: int):
    """
    Desactiva un vehículo (soft-delete).
    El vehículo no se elimina, solo se marca como inactivo.
    """
    ok = await delete_vehicle(vehicle_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return None