from fastapi import APIRouter, Depends, HTTPException, Query
from propiedad_horizontal.app.schemas.parking_assignment import MonthlyAssignmentCreate, MonthlyAssignmentRead
from propiedad_horizontal.app.services.parking_assignment_service import (
    create_monthly_assignment, list_assignments, get_assignment, cancel_assignment
)
from propiedad_horizontal.app.core.auth import require_permissions
#asignar 1–6 meses, cancelar, listar)
router = APIRouter(prefix="/parking/assignments", tags=["parking-assignments"])

@router.get("/", response_model=list[MonthlyAssignmentRead], dependencies=[Depends(require_permissions(["parking:read"]))])
async def list_assignments_endpoint(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    assignments = await list_assignments(limit=limit, offset=offset)
    out = []
    for a in assignments:
        dto = MonthlyAssignmentRead.model_validate(a)
        dto.persona_id = a.persona_id  # usar el ID directo sin acceder a la relación
        dto.vehicle_type_id = a.vehicle_type_id
        out.append(dto)
    return out

@router.get("/{assignment_id}", response_model=MonthlyAssignmentRead, dependencies=[Depends(require_permissions(["parking:read"]))])
async def get_assignment_endpoint(assignment_id: int):
    a = await get_assignment(assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    dto = MonthlyAssignmentRead.model_validate(a)
    dto.persona_id = a.persona.id
    dto.vehicle_type_id = a.vehicle_type_id
    return dto

@router.post("/", response_model=MonthlyAssignmentRead, status_code=201, dependencies=[Depends(require_permissions(["parking:write"]))])
async def create_assignment_endpoint(payload: MonthlyAssignmentCreate):
    try:
        a = await create_monthly_assignment(payload)
        dto = MonthlyAssignmentRead.model_validate(a)
        dto.persona_id = a.persona.id
        dto.vehicle_type_id = a.vehicle_type_id
        return dto
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{assignment_id}/cancel", status_code=204, dependencies=[Depends(require_permissions(["parking:write"]))])
async def cancel_assignment_endpoint(assignment_id: int):
    ok = await cancel_assignment(assignment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return None
