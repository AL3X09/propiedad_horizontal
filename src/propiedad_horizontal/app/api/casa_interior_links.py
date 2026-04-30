from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from propiedad_horizontal.app.schemas.casa_interior_link import (
    CasaInteriorLinkCreate, CasaInteriorLinkUpdate, CasaInteriorLinkRead
)
from propiedad_horizontal.app.services.casa_interior_link_service import (
    create_link, get_torrecasa_id, list_links, get_link, update_link, deactivate_link
)
from propiedad_horizontal.app.domain.enums import ApartmentStatus
from propiedad_horizontal.app.core.auth import require_permissions

router = APIRouter(prefix="/casa-interior-links", tags=["casa-interior-links"])
#vinculosinteriorcasa
@router.get("/", response_model=list[CasaInteriorLinkRead], dependencies=[Depends(require_permissions(["vinculosinteriorcasa:read"]))])
async def list_links_endpoint(
    casa_apartamento_id: Optional[int] = None,
    torre_interior_id: Optional[int] = None,
    status: Optional[ApartmentStatus] = None,
    active_only: bool = True,
    limit: int = Query(100, ge=1, le=800),
    offset: int = Query(0, ge=0),
):
    items = await list_links(
        casa_apartamento_id=casa_apartamento_id,
        torre_interior_id=torre_interior_id,
        status=status,
        active_only=active_only,
        limit=limit,
        offset=offset,
    )
    return [CasaInteriorLinkRead.model_validate(i) for i in items]

@router.get("/{link_id}", response_model=CasaInteriorLinkRead, dependencies=[Depends(require_permissions(["vinculosinteriorcasa:read"]))])
async def get_link_endpoint(link_id: int):
    i = await get_link(link_id)
    if not i:
        raise HTTPException(status_code=404, detail="Vínculo no encontrado")
    return CasaInteriorLinkRead.model_validate(i)

@router.get("/{interiortorre}/id", response_model=int, dependencies=[Depends(require_permissions(["vinculosinteriorcasa:read"]))])
async def get_interiortorre_id_endpoint(id_casa_apto: int, id_interior_torre: int):
    tc_id = await get_torrecasa_id(id_casa_apto, id_interior_torre)
    if tc_id is None:
        raise HTTPException(status_code=404, detail="relación torre/interior casa/apto no encontrada")
    return tc_id

@router.get("/{interiortorre}/id", response_model=int, dependencies=[Depends(require_permissions(["vinculosinteriorcasa:read"]))])
async def get_interiortorre_id_endpoint(id_interior_torre: int):
    tc_id = await get_torrecasa_id(id_interior_torre)
    if tc_id is None:
        raise HTTPException(status_code=404, detail="relación torre/interior no encontrada")
    return tc_id

@router.get("/{casaapartamento}/id", response_model=int, dependencies=[Depends(require_permissions(["vinculosinteriorcasa:read"]))])
async def get_casaapartamento_id_endpoint(id_casa_apto: int):
    tc_id = await get_torrecasa_id(id_casa_apto)
    if tc_id is None:
        raise HTTPException(status_code=404, detail="relación casa/apto no encontrada")
    return tc_id

@router.post("/", response_model=CasaInteriorLinkRead, status_code=201, dependencies=[Depends(require_permissions(["vinculosinteriorcasa:write"]))])
async def create_link_endpoint(payload: CasaInteriorLinkCreate):
    try:
        i = await create_link(payload)
        return CasaInteriorLinkRead.model_validate(i)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.patch("/{link_id}", response_model=CasaInteriorLinkRead, dependencies=[Depends(require_permissions(["vinculosinteriorcasa:write"]))])
async def update_link_endpoint(link_id: int, payload: CasaInteriorLinkUpdate):
    i = await update_link(link_id, payload)
    if not i:
        raise HTTPException(status_code=404, detail="Vínculo no encontrado")
    return CasaInteriorLinkRead.model_validate(i)

@router.post("/{link_id}/deactivate", status_code=204, dependencies=[Depends(require_permissions(["vinculosinteriorcasa:write"]))])
async def deactivate_link_endpoint(link_id: int):
    ok = await deactivate_link(link_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Vínculo no encontrado")
    return None
