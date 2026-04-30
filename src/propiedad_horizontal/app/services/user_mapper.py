from propiedad_horizontal.app.models.user import User
from propiedad_horizontal.app.schemas.permission import PermissionRead
from propiedad_horizontal.app.schemas.role import RoleRead
from propiedad_horizontal.app.schemas.user import UserRead

async def to_user_read(user: User) -> UserRead:
    role_perms = []
    role = None
    if user.role:
        role_perms = [PermissionRead(id=p.id, code=p.code, description=p.description) 
                      for p in await user.role.permissions.all()]
        role = RoleRead(
            id=user.role.id,
            name=user.role.name,
            description=user.role.description,
            permissions=role_perms,
        )

    return UserRead(
        id=user.id,
        username=user.username,
        is_active=user.is_active,
        role=role,
        must_change_password=user.must_change_password,
        password_changed_at=user.password_changed_at,
        permissions=[p.code for p in role_perms],
    )
