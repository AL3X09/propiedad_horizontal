from fastapi import APIRouter, Depends, HTTPException, Query
from propiedad_horizontal.app.schemas.bien import (
    BienCreate,
    BienUpdate,
    BienRead,
    BienToggle,
)
from propiedad_horizontal.app.services.bien_service import (
    create_bien,
    list_bienes,
    get_bien,
    update_bien,
    toggle_bien,
    delete_bien,
)
from propiedad_horizontal.app.core.auth import require_permissions

router = APIRouter(prefix="/bienes", tags=["bienes"])


@router.get("", response_model=list[BienRead], dependencies=[Depends(require_permissions(["bienes:read"]))])
async def list_bienes_endpoint(
    tipo: str | None = Query(None, description="Filtrar por tipo"),
    include_inactive: bool = Query(False, description="Incluir bienes inactivos"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    bienes = await list_bienes(
        tipo=tipo,
        include_inactive=include_inactive,
        limit=limit,
        offset=offset,
    )
    out: list[BienRead] = []
    for bien in bienes:
        dto = BienRead.model_validate(bien)
        out.append(dto)
    return out


@router.get("/active", response_model=list[BienRead])
async def list_active_bienes_endpoint():
    bienes = await list_bienes(include_inactive=False, limit=100, offset=0)
    out: list[BienRead] = []
    for bien in bienes:
        dto = BienRead.model_validate(bien)
        out.append(dto)
    return out


@router.get("/{bien_id}", response_model=BienRead, dependencies=[Depends(require_permissions(["bienes:read"]))])
async def get_bien_endpoint(bien_id: int):
    bien = await get_bien(bien_id)
    if not bien:
        raise HTTPException(status_code=404, detail="Bien no encontrado")
    dto = BienRead.model_validate(bien)
    return dto


@router.post("", response_model=BienRead, status_code=201, dependencies=[Depends(require_permissions(["bienes:write"]))])
async def create_bien_endpoint(payload: BienCreate):
    try:
        bien = await create_bien(payload)
        dto = BienRead.model_validate(bien)
        dto.usuario_ids = [u.id for u in bien.usuarios]
        return dto
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{bien_id}", response_model=BienRead, dependencies=[Depends(require_permissions(["bienes:write"]))])
async def update_bien_endpoint(bien_id: int, payload: BienUpdate):
    try:
        bien = await update_bien(bien_id, payload)
        if not bien:
            raise HTTPException(status_code=404, detail="Bien no encontrado")
        dto = BienRead.model_validate(bien)
        return dto
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{bien_id}/toggle", response_model=BienRead, dependencies=[Depends(require_permissions(["bienes:write"]))])
async def toggle_bien_endpoint(bien_id: int, payload: BienToggle):
    bien = await toggle_bien(bien_id, payload.is_active)
    if not bien:
        raise HTTPException(status_code=404, detail="Bien no encontrado")
    dto = BienRead.model_validate(bien)
    dto.usuario_ids = [u.id for u in bien.usuarios]
    return dto


@router.delete("/{bien_id}", status_code=204, dependencies=[Depends(require_permissions(["bienes:write"]))])
async def delete_bien_endpoint(bien_id: int):
    ok = await delete_bien(bien_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Bien no encontrado")
    return None
