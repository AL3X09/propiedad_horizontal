from fastapi import APIRouter, HTTPException, Query, Depends, status
from propiedad_horizontal.app.schemas.user import (
    UserCreate, UserUpdate, UserRead,
    PasswordChangeRequest, ForcePasswordChangeRequest   # 👈 Asegúrate de importar LoginRequest
)
from propiedad_horizontal.app.services.user_service import (
    create_user, get_user, list_users, update_user, delete_user, change_password, force_change_password
)
from propiedad_horizontal.app.services.user_mapper import to_user_read
from propiedad_horizontal.app.core.auth import require_permissions, get_current_user
from propiedad_horizontal.app.core.security import create_access_token

router = APIRouter(prefix="/users", tags=["users"])

# ----------------- YO -----------------
@router.get("/me", response_model=UserRead)
async def read_me(current_user=Depends(get_current_user)):
    return await to_user_read(current_user)

# ----------------- LISTAR -----------------
@router.get("/", response_model=list[UserRead], dependencies=[Depends(require_permissions(["users:read"]))])
async def list_users_endpoint(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    users = await list_users(limit=limit, offset=offset)
    out: list[UserRead] = []
    for u in users:
        out.append(await to_user_read(u))
    return out

# ----------------- OBTENER -----------------
@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(require_permissions(["users:read"]))])
async def get_user_endpoint(user_id: int):
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return await to_user_read(user)

# ----------------- CREAR -----------------
@router.post("/", response_model=UserRead, status_code=201, dependencies=[Depends(require_permissions(["users:write"]))])
async def create_user_endpoint(payload: UserCreate):
    try:
        user = await create_user(payload)
        return await to_user_read(user)   # 👈 nunca model_validate(user) por M2M
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

# ----------------- CREAR -----------------
@router.post("/crearadmin", response_model=UserRead, status_code=201)
async def create_user_endpoint(payload: UserCreate):
    try:
        user = await create_user(payload)
        return await to_user_read(user)   # 👈 nunca model_validate(user) por M2M
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

# ----------------- ACTUALIZAR -----------------
@router.patch("/{user_id}", response_model=UserRead, dependencies=[Depends(require_permissions(["users:write"]))])
async def update_user_endpoint(user_id: int, payload: UserUpdate):
    user = await update_user(user_id, payload)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return await to_user_read(user)

# Compatibilidad PUT (clientes que usan PUT para actualizar entre versiones)
@router.put("/{user_id}", response_model=UserRead, dependencies=[Depends(require_permissions(["users:write"]))])
async def update_user_via_put_endpoint(user_id: int, payload: UserUpdate):
    user = await update_user(user_id, payload)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return await to_user_read(user)

# ----------------- ELIMINAR -----------------
@router.delete("/{user_id}", status_code=204, dependencies=[Depends(require_permissions(["users:write"]))])
async def delete_user_endpoint(user_id: int):
    ok = await delete_user(user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return None

# ----------------- CAMBIAR CONTRASEÑA (normal) -----------------
@router.post("/change-password", response_model=dict)
async def change_password_endpoint(
    payload: PasswordChangeRequest,
    current_user = Depends(get_current_user)
):
    """Cambio de contraseña normal (requiere contraseña actual)"""
    success = await change_password(
        current_user,
        payload.current_password,
        payload.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña actual incorrecta"
        )
    return {"message": "Contraseña cambiada exitosamente"}

# ----------------- CAMBIO FORZADO PRIMER LOGIN -----------------
@router.post("/force-change-password", response_model=dict)
async def force_change_password_endpoint(
    payload: ForcePasswordChangeRequest,
    current_user = Depends(get_current_user)
):
    """Cambio de contraseña forzado (primer login)"""
    if not current_user.must_change_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No es necesario cambiar la contraseña"
        )

    await force_change_password(current_user, payload.new_password)
    return {"message": "Contraseña cambiada exitosamente"}