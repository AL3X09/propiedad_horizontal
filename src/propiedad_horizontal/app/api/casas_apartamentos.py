from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from propiedad_horizontal.app.schemas.casa_apartamento import (
    CasaApartamentoCreate, CasaApartamentoUpdate, CasaApartamentoRead
)
from propiedad_horizontal.app.services.casa_apartamento_service import (
    create_casa_apartamento, get_id_casa_apartammento, list_casas_apartamentos, get_casa_apartamento, update_casa_apartamento, deactivate_casa_apartamento
)
from propiedad_horizontal.app.core.auth import require_permissions

router = APIRouter(prefix="/casas-apartamentos", tags=["casas-apartamentos"])

@router.get("/", response_model=list[CasaApartamentoRead])
async def list_casas_apartamentos_endpoint(
    q: Optional[str] = None,
    active_only: bool = True,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    items = await list_casas_apartamentos(q=q, active_only=active_only, limit=limit, offset=offset)
    return [CasaApartamentoRead.model_validate(i) for i in items]

@router.get("/{item_id}", response_model=CasaApartamentoRead, dependencies=[Depends(require_permissions(["house_apartment:read"]))])
async def get_casa_apartamento_endpoint(item_id: int):
    i = await get_casa_apartamento(item_id)
    if not i:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return CasaApartamentoRead.model_validate(i)

@router.get("/{c_numero_letra}/id", response_model=int)
async def get_c_numero_letra_id_endpoint(c_numero_letra: str):
    c_id = await get_id_casa_apartammento(c_numero_letra)
    if c_id is None:
        raise HTTPException(status_code=404, detail="Casa o apartamento no encontrada")
    return c_id

@router.post("/", response_model=CasaApartamentoRead, status_code=201, dependencies=[Depends(require_permissions(["house_apartment:write"]))])
async def create_casa_apartamento_endpoint(payload: CasaApartamentoCreate):
    try:
        i = await create_casa_apartamento(payload)
        return CasaApartamentoRead.model_validate(i)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.patch("/{item_id}", response_model=CasaApartamentoRead, dependencies=[Depends(require_permissions(["house_apartment:write"]))])
async def update_casa_apartamento_endpoint(item_id: int, payload: CasaApartamentoUpdate):
    try:
        i = await update_casa_apartamento(item_id, payload)
        if not i:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        return CasaApartamentoRead.model_validate(i)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.post("/{item_id}/deactivate", status_code=204, dependencies=[Depends(require_permissions(["house_apartment:write"]))])
async def deactivate_casa_apartamento_endpoint(item_id: int):
    ok = await deactivate_casa_apartamento(item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return None
