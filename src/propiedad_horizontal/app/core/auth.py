from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Callable, List
from propiedad_horizontal.app.core.security import decode_token, create_access_token
from propiedad_horizontal.app.models.user import User
import logging

logger = logging.getLogger(__name__)
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # 👈 apúntalo aquí

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login/form", auto_error=False)  # tokenUrl opcional


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    logger.info(f"🔍 Token recibido: {token[:50]}...")  # Primeros 50 caracteres
    logger.info(f"📏 Longitud del token: {len(token)}")
    
    payload = decode_token(token)
    if not payload:
        logger.error(f"❌ Token inválido o no se pudo decodificar")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token inválido o expirado"
        )
    
    sub = payload.get("sub")
    logger.info(f"👤 Username extraído: {sub}")
    
    if not sub:
        logger.error(f"❌ Token inválido o no se pudo decodificar")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token inválido o expirado"
        )
    
    logger.info(f"🔎 Buscando usuario: {sub}")
    user = await User.get_or_none(username=sub).prefetch_related("role", "role__permissions")
    
    if not user:
        logger.error(f"❌ Usuario '{sub}' no encontrado en BD")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Usuario no encontrado"
        )
    
    if not user.is_active:
        logger.error(f"❌ Usuario '{sub}' no está activo")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Usuario no está activo"
        )
    
    logger.info(f"✅ Usuario autorizado: {sub}")
    return user

def require_roles(*roles: str) -> Callable:
    async def _dep(user: User = Depends(get_current_user)) -> User:
        role_name = getattr(user.role, "name", None)
        if role_name is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol insuficiente")
        allowed_names = {role.lower() for role in roles}
        if role_name.lower() in allowed_names or role_name.lower() == "superadmin":
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol insuficiente")
    return _dep


def optional_token(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependencia opcional que obtiene el token del header Authorization.
    Retorna None si no está presente (no lanza error).
    """
    return token


def require_permissions(required: list[str]):
    """
    Superadmin bypass: si el rol es SUPERADMIN, se permite todo sin revisar permisos.
    En caso contrario, exige que el rol del usuario tenga TODOS los permisos de 'required'.
    Soporta tokens anónimos para formularios públicos.
    """
    async def _dep(token: str = Depends(optional_token), request: Request = None) -> User:
        # Si no hay token, retornar error 401
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")
        
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        
        # Permitir tokens anónimos solo para parking:write
        if payload.get("sub") == "anonymous":
            if "parking:write" not in required:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes para token anónimo")
            # Validar IP matches
            client_ip = request.client.host if request else None
            if payload.get("ip") != client_ip:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="IP mismatch")
            # Retornar un usuario dummy o None, ya que no hay usuario real
            return None
        
        # Lógica normal para usuarios autenticados
        sub = payload.get("sub")
        user = await User.get_or_none(username=sub).prefetch_related("role", "role__permissions")
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado o inactivo")
        
        role_name = getattr(user.role, "name", None)
        if role_name and role_name.lower() == "superadmin":
            return user
        
        if not user.role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes")
        
        role_perms = {p.code for p in await user.role.permissions.all()}
        if all(p in role_perms for p in required):
            return user
        
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes")
    return _dep

