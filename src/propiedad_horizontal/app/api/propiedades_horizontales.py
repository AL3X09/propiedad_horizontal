from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from propiedad_horizontal.app.schemas.propiedad_horizontal import (
    PropiedadHorizontalCreate, PropiedadHorizontalRead, PropiedadHorizontalUpdate
)
from propiedad_horizontal.app.services.propiedad_horizontal_service import (
    create_ph, list_ph, get_ph, update_ph
)
from propiedad_horizontal.app.core.auth import require_permissions

router = APIRouter(prefix="/ph", tags=["propiedad-horizontal"])

@router.get("/", response_model=list[PropiedadHorizontalRead], dependencies=[Depends(require_permissions(["ph:read"]))])
async def list_ph_endpoint(
    nombre: Optional[str] = None,
    localidad: Optional[str] = None,
    barrio: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    items = await list_ph(nombre=nombre, localidad=localidad, barrio=barrio, limit=limit, offset=offset)
    return [PropiedadHorizontalRead.model_validate(i) for i in items]

@router.get("/{ph_id}", response_model=PropiedadHorizontalRead, dependencies=[Depends(require_permissions(["ph:read"]))])
async def get_ph_endpoint(ph_id: int):
    ph = await get_ph(ph_id)
    if not ph:
        raise HTTPException(status_code=404, detail="Propiedad Horizontal no encontrada")
    return PropiedadHorizontalRead.model_validate(ph)

@router.post("/", response_model=PropiedadHorizontalRead, status_code=201, dependencies=[Depends(require_permissions(["ph:write"]))])
async def create_ph_endpoint(payload: PropiedadHorizontalCreate):
    ph = await create_ph(payload)
    return PropiedadHorizontalRead.model_validate(ph)

@router.patch("/{ph_id}", response_model=PropiedadHorizontalRead, dependencies=[Depends(require_permissions(["ph:write"]))])
async def update_ph_endpoint(ph_id: int, payload: PropiedadHorizontalUpdate):
    ph = await update_ph(ph_id, payload)
    if not ph:
        raise HTTPException(status_code=404, detail="Propiedad Horizontal no encontrada")
    return PropiedadHorizontalRead.model_validate(ph)
