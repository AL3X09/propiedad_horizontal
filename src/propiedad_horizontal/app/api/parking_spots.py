from fastapi import APIRouter, Depends, HTTPException, Query
from propiedad_horizontal.app.schemas.parking import ParkingSpotCreate, ParkingSpotUpdate, ParkingSpotRead
from propiedad_horizontal.app.services.parking_service import (
    create_spot, list_spots, get_spot, update_spot, deactivate_spot
)
from propiedad_horizontal.app.domain.enums.parking_spot_status import ParkingSpotStatus
from propiedad_horizontal.app.core.auth import require_permissions

router = APIRouter(prefix="/parking/spots", tags=["parking-spots"])

@router.get("/", response_model=list[ParkingSpotRead], dependencies=[Depends(require_permissions(["parking:read"]))])
async def list_spots_endpoint(
    vehicle_type_id: int | None = None,
    parking_status : ParkingSpotStatus | None = None,
    is_parking_public: bool | None = None,
    active_only: bool = True,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    spots = await list_spots(vehicle_type_id=vehicle_type_id, parking_status=parking_status, is_parking_public=is_parking_public, active_only=active_only, limit=limit, offset=offset)
    out = []
    for s in spots:
        dto = ParkingSpotRead.model_validate(s)
        dto.vehicle_type_id = s.vehicle_type_id
        out.append(dto)
    return out

@router.get("/disponibles", response_model=list[ParkingSpotRead], dependencies=[Depends(require_permissions(["parking:read"]))])
async def list_spot_disponible(
    vehicle_type_id: int,
    parking_status : ParkingSpotStatus,
    is_parking_public: bool = False,
    active_only: bool = True,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    spots = await list_spots(vehicle_type_id=vehicle_type_id, parking_status=parking_status, is_parking_public=is_parking_public, active_only=active_only, limit=limit, offset=offset)
    out = []
    for s in spots:
        dto = ParkingSpotRead.model_validate(s)
        dto.vehicle_type_id = s.vehicle_type_id
        out.append(dto)
    return out

@router.get("/disponibles/publicos", response_model=list[ParkingSpotRead], dependencies=[Depends(require_permissions(["parking:read"]))])
async def list_spot_disponible(
    vehicle_type_id: int,
    parking_status : ParkingSpotStatus,
    active_only: bool = True,
    is_parking_public: bool = True,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    spots = await list_spots(vehicle_type_id=vehicle_type_id, parking_status=parking_status, is_parking_public=is_parking_public, active_only=active_only, limit=limit, offset=offset)
    out = []
    for s in spots:
        dto = ParkingSpotRead.model_validate(s)
        dto.vehicle_type_id = s.vehicle_type_id
        out.append(dto)
    return out

@router.post("/", response_model=ParkingSpotRead, status_code=201)
async def create_spot_endpoint(payload: ParkingSpotCreate):
    try:
        spot = await create_spot(payload)
        dto = ParkingSpotRead.model_validate(spot)
        dto.vehicle_type_id = spot.vehicle_type_id
        return dto
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.patch("/{spot_id}", response_model=ParkingSpotRead, dependencies=[Depends(require_permissions(["parking:write"]))])
async def update_spot_endpoint(spot_id: int, payload: ParkingSpotUpdate):
    spot = await update_spot(spot_id, payload)
    if not spot:
        raise HTTPException(status_code=404, detail="Parqueadero no encontrado")
    dto = ParkingSpotRead.model_validate(spot)
    dto.vehicle_type_id = spot.vehicle_type_id
    return dto

@router.post("/{spot_id}/deactivate", status_code=204, dependencies=[Depends(require_permissions(["parking:write"]))])
async def deactivate_spot_endpoint(spot_id: int):
    ok = await deactivate_spot(spot_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Parqueadero no encontrado")
    return None