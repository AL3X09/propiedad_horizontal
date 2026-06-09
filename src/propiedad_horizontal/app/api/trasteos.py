from fastapi import APIRouter, HTTPException, Query, Depends, status
from datetime import datetime
from propiedad_horizontal.app.schemas.trasteo import (
    TrasteoCreate,
    TrasteoUpdate,
    TrasteoRead,
    TrasteoReadDetail,
    TrasteoBienCreate,
    TrasteoBienRead,
)
from propiedad_horizontal.app.services.trasteo_service import (
    create_trasteo,
    list_trasteos,
    get_trasteo,
    get_trasteo_with_bienes,
    update_trasteo,
    delete_trasteo,
    add_bien_to_trasteo,
    update_trasteo_bien_cantidad,
    remove_bien_from_trasteo,
    authorize_trasteo,
    get_bienes_by_usuario,
)
from propiedad_horizontal.app.core.auth import require_permissions, get_current_user

router = APIRouter(prefix="/trasteos", tags=["trasteos"])


# ============== TRASTEOS MAIN ENDPOINTS ==============

@router.post("", response_model=TrasteoReadDetail, status_code=201, dependencies=[Depends(require_permissions(["trasteos:write"]))])
async def create_trasteo_endpoint(payload: TrasteoCreate):
    """Crear un nuevo trasteo con listado de bienes"""
    try:
        trasteo = await create_trasteo(payload)
        # Obtener con detalles de bienes
        result = await get_trasteo_with_bienes(trasteo.id)
        if result:
            return {
                **result["trasteo"].__dict__,
                "bienes": result["bienes"],
            }
        return trasteo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[TrasteoRead], dependencies=[Depends(require_permissions(["trasteos:read"]))])
async def list_trasteos_endpoint(
    usuario_id: int | None = Query(None, description="Filtrar por usuario_id"),
    is_autorizado: bool | None = Query(None, description="Filtrar por estado de autorización"),
    include_inactive: bool = Query(False, description="Incluir trasteos inactivos"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Listar trasteos con filtros opcionales"""
    trasteos = await list_trasteos(
        usuario_id=usuario_id,
        is_autorizado=is_autorizado,
        include_inactive=include_inactive,
        limit=limit,
        offset=offset,
    )
    out: list[TrasteoRead] = []
    for t in trasteos:
        dto = TrasteoRead.model_validate(t)
        out.append(dto)
    return out


@router.get("/{trasteo_id}", response_model=TrasteoReadDetail, dependencies=[Depends(require_permissions(["trasteos:read"]))])
async def get_trasteo_endpoint(trasteo_id: int):
    """Obtener un trasteo con detalles de sus bienes"""
    result = await get_trasteo_with_bienes(trasteo_id)
    if not result:
        raise HTTPException(status_code=404, detail="Trasteo no encontrado")
    
    return {
        **result["trasteo"].__dict__,
        "bienes": result["bienes"],
    }


@router.patch("/{trasteo_id}", response_model=TrasteoReadDetail, dependencies=[Depends(require_permissions(["trasteos:write"]))])
async def update_trasteo_endpoint(trasteo_id: int, payload: TrasteoUpdate):
    """Actualizar un trasteo y opcionalmente sus bienes"""
    try:
        trasteo = await update_trasteo(trasteo_id, payload)
        if not trasteo:
            raise HTTPException(status_code=404, detail="Trasteo no encontrado")
        
        result = await get_trasteo_with_bienes(trasteo_id)
        if result:
            return {
                **result["trasteo"].__dict__,
                "bienes": result["bienes"],
            }
        return trasteo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{trasteo_id}", status_code=204, dependencies=[Depends(require_permissions(["trasteos:write"]))])
async def delete_trasteo_endpoint(trasteo_id: int):
    """Eliminar (soft delete) un trasteo"""
    ok = await delete_trasteo(trasteo_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Trasteo no encontrado")
    return None


@router.post("/{trasteo_id}/authorize", response_model=TrasteoReadDetail, dependencies=[Depends(require_permissions(["trasteos:authorize"]))])
async def authorize_trasteo_endpoint(trasteo_id: int):
    """Autorizar un trasteo"""
    trasteo = await authorize_trasteo(trasteo_id)
    if not trasteo:
        raise HTTPException(status_code=404, detail="Trasteo no encontrado")
    
    result = await get_trasteo_with_bienes(trasteo_id)
    if result:
        return {
            **result["trasteo"].__dict__,
            "bienes": result["bienes"],
        }
    return trasteo


# ============== BIENES EN TRASTEO ENDPOINTS ==============

@router.post("/{trasteo_id}/bienes", response_model=TrasteoBienRead, status_code=201, dependencies=[Depends(require_permissions(["trasteos:write"]))])
async def add_bien_to_trasteo_endpoint(trasteo_id: int, payload: TrasteoBienCreate):
    """Agregar un bien a un trasteo existente"""
    try:
        trasteo_bien = await add_bien_to_trasteo(trasteo_id, payload)
        if not trasteo_bien:
            raise HTTPException(status_code=404, detail="Trasteo no encontrado")
        
        dto = TrasteoBienRead.model_validate(trasteo_bien)
        return dto
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{trasteo_id}/bienes/{trasteo_bien_id}/cantidad", response_model=TrasteoBienRead, dependencies=[Depends(require_permissions(["trasteos:write"]))])
async def update_bien_cantidad_endpoint(
    trasteo_id: int,
    trasteo_bien_id: int,
    nueva_cantidad: int = Query(..., ge=1, description="Nueva cantidad"),
):
    """Actualizar la cantidad de un bien en un trasteo"""
    try:
        trasteo_bien = await update_trasteo_bien_cantidad(trasteo_bien_id, nueva_cantidad)
        if not trasteo_bien:
            raise HTTPException(status_code=404, detail="Bien en trasteo no encontrado")
        
        dto = TrasteoBienRead.model_validate(trasteo_bien)
        return dto
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{trasteo_id}/bienes/{trasteo_bien_id}", status_code=204, dependencies=[Depends(require_permissions(["trasteos:write"]))])
async def remove_bien_from_trasteo_endpoint(trasteo_id: int, trasteo_bien_id: int):
    """Eliminar un bien de un trasteo"""
    ok = await remove_bien_from_trasteo(trasteo_bien_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Bien en trasteo no encontrado")
    return None


# ============== USUARIO BIENES ENDPOINTS ==============

@router.get("/usuario/{usuario_id}/bienes", dependencies=[Depends(require_permissions(["trasteos:read"]))])
async def get_usuario_bienes_endpoint(usuario_id: int):
    """Obtener todos los bienes de un usuario a través de sus trasteos activos (con cantidades totales)"""
    bienes = await get_bienes_by_usuario(usuario_id)
    return {
        "usuario_id": usuario_id,
        "bienes": bienes,
        "total_bienes": len(bienes),
    }
