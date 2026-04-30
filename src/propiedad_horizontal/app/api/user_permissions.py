from fastapi import APIRouter, Depends, HTTPException
from propiedad_horizontal.app.schemas.user_permissions import UserPermissionsSet
from propiedad_horizontal.app.schemas.user import UserRead
from propiedad_horizontal.app.services.user_permission_service import set_permissions_by_username
from propiedad_horizontal.app.services.user_mapper import to_user_read
from propiedad_horizontal.app.core.auth import require_permissions

router = APIRouter(prefix="/users", tags=["user-permissions"])

@router.post("/{username}/permissions", response_model=UserRead, dependencies=[Depends(require_permissions(["permissions:write"]))])
async def set_user_permissions_endpoint(username: str, payload: UserPermissionsSet):
    try:
        user = await set_permissions_by_username(username, payload.permissions)
        return await to_user_read(user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))