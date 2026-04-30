from typing import List, Optional
from tortoise.exceptions import IntegrityError
from propiedad_horizontal.app.models.permission import Permission
from propiedad_horizontal.app.schemas.permission import PermissionCreate, PermissionUpdate

async def create_permission(data: PermissionCreate) -> Permission:
    try:
        return await Permission.create(
            code=data.code.strip(),
            description=data.description.strip() if data.description else None
        )
    except IntegrityError:
        raise ValueError("Ya existe un permiso con ese code.")

async def list_permissions(
    q: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Permission]:
    qs = Permission.all().order_by("code")
    if q:
        qs = qs.filter(code__icontains=q)
    return await qs.offset(offset).limit(limit)

async def get_permission(permission_id: int) -> Optional[Permission]:
    return await Permission.get_or_none(id=permission_id)

async def update_permission(permission_id: int, data: PermissionUpdate) -> Optional[Permission]:
    perm = await Permission.get_or_none(id=permission_id)
    if not perm:
        return None

    if data.code is not None:
        perm.code = data.code.strip()
    if data.description is not None:
        perm.description = data.description.strip() if data.description else None

    try:
        await perm.save()
        return perm
    except IntegrityError:
        raise ValueError("No se pudo actualizar: el code ya está en uso.")

async def delete_permission(permission_id: int) -> bool:
    deleted = await Permission.filter(id=permission_id).delete()
    return deleted > 0

# Utilidad que ya venías usando en User Service (la dejamos acá también)
async def ensure_permissions_exist(codes: List[str]) -> None:
    for code in codes:
        await Permission.get_or_create(code=code.strip())