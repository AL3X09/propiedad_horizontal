from fastapi import APIRouter, Depends, HTTPException, Query
from propiedad_horizontal.app.schemas.role import RoleCreate, RoleRead, RoleUpdate
from propiedad_horizontal.app.services.role_service import (
    create_role,
    delete_role,
    get_role,
    list_roles,
    update_role,
)
from propiedad_horizontal.app.core.auth import require_permissions

router = APIRouter(prefix="/roles", tags=["roles"])

# Permisos para gestionar roles:
# - roles:read
# - roles:write

@router.get("/", response_model=list[RoleRead], dependencies=[Depends(require_permissions(["roles:read"]))])
async def list_roles_endpoint(
    q: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    roles = await list_roles(q=q, limit=limit, offset=offset)
    return [RoleRead.model_validate(role) for role in roles]


@router.get("/{role_id}", response_model=RoleRead, dependencies=[Depends(require_permissions(["roles:read"]))])
async def get_role_endpoint(role_id: int):
    role = await get_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return RoleRead.model_validate(role)


@router.post("/", response_model=RoleRead, status_code=201, dependencies=[Depends(require_permissions(["roles:write"]))])
async def create_role_endpoint(payload: RoleCreate):
    try:
        role = await create_role(payload)
        return RoleRead.model_validate(role)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.patch("/{role_id}", response_model=RoleRead, dependencies=[Depends(require_permissions(["roles:write"]))])
async def update_role_endpoint(role_id: int, payload: RoleUpdate):
    try:
        role = await update_role(role_id, payload)
        if not role:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        return RoleRead.model_validate(role)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{role_id}", status_code=204, dependencies=[Depends(require_permissions(["roles:write"]))])
async def delete_role_endpoint(role_id: int):
    ok = await delete_role(role_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return None
