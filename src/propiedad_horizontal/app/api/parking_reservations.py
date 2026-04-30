from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from datetime import datetime
from math import ceil
from propiedad_horizontal.app.schemas.parking_reservation import VisitorReservationCreate, VisitorReservationRead
from propiedad_horizontal.app.services.parking_reservation_service import (
    create_reservation, list_reservations, get_reservation, cancel_reservation, complete_reservation, list_reservations_by_user_id,
    scan_qr, _find_available_spot, _has_overlap_for_spot_datetime
)
from propiedad_horizontal.app.core.auth import require_permissions
from propiedad_horizontal.app.models.vehicle_type import VehicleType
from propiedad_horizontal.app.models.casa_apartamento_interior_torre import CasaApartamentoInteriorTorre

router = APIRouter(prefix="/parking/reservations", tags=["parking-reservations"])

# ---- ENDPOINTS PROTEGIDOS ----
@router.get("/", response_model=list[VisitorReservationRead], dependencies=[Depends(require_permissions(["reservas:read"]))])
async def list_reservations_endpoint(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    reservations = await list_reservations(limit=limit, offset=offset)
    out = []
    for r in reservations:
        dto = VisitorReservationRead.model_validate(r)
        dto.vehicle_type_id = r.vehicle_type_id
        out.append(dto)
    return out

@router.get("/{reservation_id}", response_model=VisitorReservationRead, dependencies=[Depends(require_permissions(["reservas:read"]))])
async def get_reservation_endpoint(reservation_id: int):
    r = await get_reservation(reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    dto = VisitorReservationRead.model_validate(r)
    dto.vehicle_type_id = r.vehicle_type_id
    return dto    

@router.get("/role/{role}/{user_id}", response_model=list[VisitorReservationRead], dependencies=[Depends(require_permissions(["reservas:read"]))])
async def get_reservations_by_user_id_endpoint(role: str, user_id: int, limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    if role not in ["superadmin", "administrador"]:
        reservations = await list_reservations_by_user_id(user_id=user_id, limit=limit, offset=offset)
    else:
        reservations = await list_reservations(limit=limit, offset=offset)
        
    out = []
    for r in reservations:
        dto = VisitorReservationRead.model_validate(r)
        dto.vehicle_type_id = r.vehicle_type_id
        out.append(dto)
    return out

@router.get("/user/{user_id}", response_model=list[VisitorReservationRead], dependencies=[Depends(require_permissions(["reservas:read"]))])
async def get_reservations_by_user_id_endpoint(user_id: int):
    reservations = await list_reservations_by_user_id(user_id=user_id)
    out = []
    for r in reservations:
        dto = VisitorReservationRead.model_validate(r)
        dto.vehicle_type_id = r.vehicle_type_id
        out.append(dto)
    return out

@router.post("/", response_model=VisitorReservationRead, status_code=201, dependencies=[Depends(require_permissions(["reservas:write"]))])
async def create_reservation_endpoint(payload: VisitorReservationCreate, background_tasks: BackgroundTasks):
    try:
        spot = None
        if payload.spot_id and payload.spot_id > 0:
            # Si se especifica un spot específico, verificar que esté disponible
            from propiedad_horizontal.app.models.parking import ParkingSpot
            from propiedad_horizontal.app.domain.enums import ParkingSpotStatus
            requested_spot = await ParkingSpot.get_or_none(
                id=payload.spot_id,
                parking_status=ParkingSpotStatus.AVIABLE,
                vehicle_type_id=payload.vehicle_type_id,
                is_parking_public=True,
                is_active=True,
            )
            if requested_spot and not await _has_overlap_for_spot_datetime(requested_spot.id, payload.starts_at, payload.ends_at):
                spot = requested_spot
        else:
            # Buscar automáticamente un spot disponible
            spot = await _find_available_spot(payload.vehicle_type_id, payload.starts_at, payload.ends_at)
        
        if not spot:
            raise ValueError("No hay espacios disponibles para el tipo de vehículo y horario seleccionado")
        
        r = await create_reservation(
            spot_id=spot.id,
            casa_apto_interior_torre_id=payload.casa_apto_interior_torre_id,
            starts_at=payload.starts_at,
            ends_at=payload.ends_at,
            visitor_type_document=payload.visitor_type_document,
            visitor_document_number=payload.visitor_document_number,
            visitor_name=payload.visitor_name,
            visitor_email=payload.visitor_email,
            visitor_cell=payload.visitor_cell,
            vehicle_type_id=payload.vehicle_type_id,
            vehicle_code=payload.vehicle_code,
            billed_minutes=payload.billed_minutes,
            background_tasks=background_tasks,
        )
        dto = VisitorReservationRead.model_validate(r)
        dto.vehicle_type_id = r.vehicle_type_id
        return dto
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{reservation_id}/scan", response_model=VisitorReservationRead)
async def scan_qr_endpoint(reservation_id: int, token: str = Query(..., min_length=1), background_tasks: BackgroundTasks = None):
    """
    Escanea un QR de parqueadero y procesa la transición de estado.
    
    **Transiciones permitidas:**
    - ACTIVE → COMPLETED: Visitante llega al parqueadero (primer escaneo)
    - COMPLETED → FINISHED: Visitante se va (segundo escaneo)
    
    **Códigos de error:**
    - 401: Token QR inválido
    - 404: Reserva no encontrada
    - 409: Reserva ya está finalizada (no permite reescaneo)
    - 410: Reserva fue cancelada (no se puede usar)
    
    Args:
        reservation_id: ID de la reserva
        token: Token QR (generado en el email de confirmación)
        background_tasks: Para ejecutar tareas asincrónicas después de la respuesta
    
    Returns:
        VisitorReservationRead: Reserva con estado actualizado
    """
    # lector de QR llamará aquí
    if background_tasks is None:
        background_tasks = BackgroundTasks()
    return await scan_qr(reservation_id, token, background_tasks)

@router.post("/{reservation_id}/cancel", status_code=204, dependencies=[Depends(require_permissions(["reservas:write"]))])
async def cancel_reservation_endpoint(reservation_id: int):
    ok = await cancel_reservation(reservation_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return None

@router.post("/{reservation_id}/complete", status_code=204, dependencies=[Depends(require_permissions(["reservas:write"]))])
async def complete_reservation_endpoint(reservation_id: int):
    ok = await complete_reservation(reservation_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return None

