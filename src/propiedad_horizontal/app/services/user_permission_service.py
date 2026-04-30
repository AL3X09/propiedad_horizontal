from typing import List
from propiedad_horizontal.app.models.user import User
from propiedad_horizontal.app.models.permission import Permission
from propiedad_horizontal.app.services.permission_service import ensure_permissions_exist

async def set_permissions_by_username(username: str, codes: List[str]) -> User:
    user = await User.get_or_none(username=username)
    if not user:
        raise ValueError("Usuario no existe.")

    await ensure_permissions_exist(codes)
    perms = await Permission.filter(code__in=[c.strip() for c in codes])

    await user.permissions.clear()
    await user.permissions.add(*perms)
    return user