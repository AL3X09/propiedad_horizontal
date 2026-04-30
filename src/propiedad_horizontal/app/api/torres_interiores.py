from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from propiedad_horizontal.app.schemas.torre_interior import (
    TorreInteriorCreate, TorreInteriorUpdate, TorreInteriorRead
)
from propiedad_horizontal.app.services.torre_interior_service import (
    create_torre_interior, get_id_torre_interior, list_torres_interiores, get_torre_interior, update_torre_interior, deactivate_torre_interior
)
from propiedad_horizontal.app.core.auth import require_permissions

router = APIRouter(prefix="/torres-interiores", tags=["torres-interiores"])

#@router.get("/", response_model=list[TorreInteriorRead], dependencies=[Depends(require_permissions(["tower_interior:read"]))])
@router.get("/", response_model=list[TorreInteriorRead])
async def list_torres_interiores_endpoint(
    q: Optional[str] = None,
    active_only: bool = True,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    items = await list_torres_interiores(q=q, active_only=active_only, limit=limit, offset=offset)
    return [TorreInteriorRead.model_validate(i) for i in items]

@router.get("/{num_torre_interior}/id", response_model=int)
async def get_torre_interior_id_endpoint(num_torre_interior: str):
    ti_id = await get_id_torre_interior(num_torre_interior)
    if ti_id is None:
        raise HTTPException(status_code=404, detail="Torre o interior no encontrada")
    return ti_id

@router.get("/{torre_interior_id}", response_model=TorreInteriorRead, dependencies=[Depends(require_permissions(["tower_interior:read"]))])
async def get_torre_interior_endpoint(torre_interior_id: int):
    ti = await get_torre_interior(torre_interior_id)
    if not ti:
        raise HTTPException(status_code=404, detail="id Torre interior no encontrada")
    return TorreInteriorRead.model_validate(ti)


@router.post("/", response_model=TorreInteriorRead, status_code=201, dependencies=[Depends(require_permissions(["tower_interior:write"]))])
async def create_torre_interior_endpoint(payload: TorreInteriorCreate):
    try:
        ti = await create_torre_interior(payload)
        return TorreInteriorRead.model_validate(ti)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.patch("/{torre_interior_id}", response_model=TorreInteriorRead, dependencies=[Depends(require_permissions(["tower_interior:write"]))])
async def update_torre_interior_endpoint(torre_interior_id: int, payload: TorreInteriorUpdate):
    try:
        ti = await update_torre_interior(torre_interior_id, payload)
        if not ti:
            raise HTTPException(status_code=404, detail="Torre interior no encontrada")
        return TorreInteriorRead.model_validate(ti)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.post("/{torre_interior_id}/deactivate", status_code=204, dependencies=[Depends(require_permissions(["tower_interior:write"]))])
async def deactivate_torre_interior_endpoint(torre_interior_id: int):
    ok = await deactivate_torre_interior(torre_interior_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Torre interior no encontrada")
    return None
