from fastapi import APIRouter, Depends, HTTPException, Query
from propiedad_horizontal.app.schemas.permission import (
    PermissionCreate, PermissionUpdate, PermissionRead
)
from propiedad_horizontal.app.services.permission_service import (
    create_permission, list_permissions, get_permission, update_permission, delete_permission
)
from propiedad_horizontal.app.core.auth import require_permissions

router = APIRouter(prefix="/permissions", tags=["permissions"])

# Sugerencia de permisos para gestionar permisos:
# - permissions:read
# - permissions:write

@router.get("/", response_model=list[PermissionRead], dependencies=[Depends(require_permissions(["permissions:read"]))])
async def list_permissions_endpoint(
    q: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    perms = await list_permissions(q=q, limit=limit, offset=offset)
    return [PermissionRead.model_validate(p) for p in perms]

@router.get("/{permission_id}", response_model=PermissionRead, dependencies=[Depends(require_permissions(["permissions:read"]))])
async def get_permission_endpoint(permission_id: int):
    perm = await get_permission(permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    return PermissionRead.model_validate(perm)

@router.post("/", response_model=PermissionRead, status_code=201, dependencies=[Depends(require_permissions(["permissions:write"]))])
async def create_permission_endpoint(payload: PermissionCreate):
    try:
        perm = await create_permission(payload)
        return PermissionRead.model_validate(perm)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.patch("/{permission_id}", response_model=PermissionRead, dependencies=[Depends(require_permissions(["permissions:write"]))])
async def update_permission_endpoint(permission_id: int, payload: PermissionUpdate):
    try:
        perm = await update_permission(permission_id, payload)
        if not perm:
            raise HTTPException(status_code=404, detail="Permiso no encontrado")
        return PermissionRead.model_validate(perm)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/{permission_id}", status_code=204, dependencies=[Depends(require_permissions(["permissions:write"]))])
async def delete_permission_endpoint(permission_id: int):
    ok = await delete_permission(permission_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    return None