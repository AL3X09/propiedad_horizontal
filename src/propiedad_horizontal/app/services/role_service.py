from typing import List, Optional, Dict, Any
from tortoise.exceptions import IntegrityError
from propiedad_horizontal.app.models.permission import Permission
from propiedad_horizontal.app.models.role import Role
from propiedad_horizontal.app.schemas.role import RoleCreate, RoleUpdate
from propiedad_horizontal.app.schemas.permission import PermissionRead


async def _ensure_permissions_exist(codes: List[str]) -> None:
    for code in codes:
        await Permission.get_or_create(code=code.strip())


async def _get_role_permissions(role_id: int) -> List[Dict[str, Any]]:
    perms = await Permission.filter(roles__id=role_id).all()
    return [PermissionRead(id=p.id, code=p.code, description=p.description).model_dump() for p in perms]


async def _set_role_permissions(role: Role, codes: List[str]) -> None:
    await _ensure_permissions_exist(codes)
    perms = await Permission.filter(code__in=[c.strip() for c in codes]).all()
    await role.permissions.clear()
    if perms:
        await role.permissions.add(*perms)


async def _role_to_dict(role: Role, include_permissions: bool = False) -> Dict[str, Any]:
    result = {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "permissions": [],
    }
    if include_permissions:
        perms = await Permission.filter(roles__id=role.id).all()
        result["permissions"] = [
            {"id": p.id, "code": p.code, "description": p.description}
            for p in perms
        ]
    return result


async def create_role(data: RoleCreate) -> Dict[str, Any]:
    try:
        role = await Role.create(
            name=data.name.strip(),
            description=data.description.strip() if data.description else None,
        )
    except IntegrityError:
        raise ValueError("Ya existe un rol con ese nombre.")

    if data.permissions:
        await _set_role_permissions(role, data.permissions)

    return await _role_to_dict(role, include_permissions=True)


async def list_roles(
    q: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    qs = Role.all().order_by("name")
    if q:
        qs = qs.filter(name__icontains=q)
    roles = await qs.offset(offset).limit(limit)
    # Incluir permisos en el listado para que el frontend pueda mostrarlos
    return [await _role_to_dict(r, include_permissions=True) for r in roles]


async def get_role(role_id: int) -> Optional[Dict[str, Any]]:
    role = await Role.get_or_none(id=role_id)
    if not role:
        return None
    return await _role_to_dict(role, include_permissions=True)


async def update_role(role_id: int, data: RoleUpdate) -> Optional[Dict[str, Any]]:
    role = await Role.get_or_none(id=role_id)
    if not role:
        return None

    if data.name is not None:
        role.name = data.name.strip()
    if data.description is not None:
        role.description = data.description.strip() if data.description else None

    try:
        await role.save()
    except IntegrityError:
        raise ValueError("No se pudo actualizar: el nombre de rol ya está en uso.")

    if data.permissions is not None:
        await _set_role_permissions(role, data.permissions)

    return await _role_to_dict(role, include_permissions=True)


async def delete_role(role_id: int) -> bool:
    deleted = await Role.filter(id=role_id).delete()
    return deleted > 0
