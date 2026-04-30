from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from tortoise.exceptions import IntegrityError
from propiedad_horizontal.app.models.user import User
from propiedad_horizontal.app.models.role import Role
from propiedad_horizontal.app.schemas.user import UserCreate, UserUpdate
from propiedad_horizontal.app.core.security import hash_password, verify_password
from propiedad_horizontal.app.core.config import APP_TIMEZONE

# Usar el timezone global de la aplicación
BOGOTA_TZ = ZoneInfo(APP_TIMEZONE)
DEFAULT_ROLE_NAME = "propietario"
ADMIN_ROLE_NAME = "superadmin"


async def _resolve_role(role_id: Optional[int]) -> Role:
    if role_id is not None:
        role = await Role.get_or_none(id=role_id)
        if not role:
            raise ValueError("Rol no existe.")
        return role

    role = await Role.get_or_none(name=DEFAULT_ROLE_NAME)
    if not role:
        raise ValueError("Rol por defecto no encontrado.")
    return role


async def create_user(data: UserCreate) -> User:
    try:
        role = await _resolve_role(data.role_id)
        must_change = role.name.lower() != ADMIN_ROLE_NAME
        user = await User.create(
            username=data.username,
            password_hash=hash_password(data.password),
            role=role,
            is_active=True,
            must_change_password=must_change,
            password_changed_at=None,
        )
        return user
    except IntegrityError:
        raise ValueError("El username ya existe.")

async def update_user(user_id: int, data: UserUpdate) -> Optional[User]:
    user = await User.get_or_none(id=user_id)
    if not user:
        return None

    if data.is_active is not None:
        user.is_active = data.is_active
    if data.role_id is not None:
        user.role = await _resolve_role(data.role_id)
    if data.password is not None:
        user.password_hash = hash_password(data.password)
        user.must_change_password = False
        user.password_changed_at = datetime.now(BOGOTA_TZ)
    if data.must_change_password is not None:
        user.must_change_password = data.must_change_password
    if data.must_change_password:
        user.password_changed_at = None

    await user.save()
    return user


async def get_user(user_id: int) -> Optional[User]:
    return await User.get_or_none(id=user_id).prefetch_related("role", "role__permissions")

async def list_users(limit: int = 50, offset: int = 0) -> List[User]:
    return (
        await User.all()
        .prefetch_related("role", "role__permissions")
        .offset(offset)
        .limit(limit)
        .order_by("-id")
    )


async def delete_user(user_id: int) -> bool:
    deleted = await User.filter(id=user_id).delete()
    return deleted > 0

async def authenticate(username: str, password: str) -> Optional[User]:
    user = await User.get_or_none(username=username).prefetch_related("role", "role__permissions")
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

async def change_password(
    user: User, 
    current_password: str, 
    new_password: str
) -> bool:
    """Cambio de contraseña normal (requiere contraseña actual)"""
    if not verify_password(current_password, user.password_hash):
        return False
    
    user.password_hash = hash_password(new_password)
    user.password_changed_at = datetime.now(BOGOTA_TZ)
    user.must_change_password = False
    await user.save()
    return True

async def force_change_password(user: User, new_password: str) -> None:
    """Cambio de contraseña forzado (primer login, no requiere contraseña actual)"""
    user.password_hash = hash_password(new_password)
    user.password_changed_at = datetime.now(BOGOTA_TZ)
    user.must_change_password = False
    await user.save()