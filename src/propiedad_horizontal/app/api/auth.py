from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from propiedad_horizontal.app.schemas.user import LoginRequest, Token, UserCreate, UserRead
from propiedad_horizontal.app.services.user_service import create_user, authenticate
from propiedad_horizontal.app.services.user_mapper import to_user_read
from propiedad_horizontal.app.core.security import create_access_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=201)
async def register(payload: UserCreate):
    """
    Registro de nuevo usuario con JSON.
    
    Campos:
      - username: str (obligatorio)
      - password: str (obligatorio)
      - role_id: int (opcional, asigna un rol existente a la cuenta)
    """
    try:
        user = await create_user(payload)
        return await to_user_read(user)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


# ----------------- REGISTER (FORM) -----------------
@router.post("/register/form", response_model=UserRead, status_code=201, tags=["auth"])
async def register_form_endpoint(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Registro de nuevo usuario con Form-Data (compatible con el botón 'Authorize' de Swagger).
    
    Usa los campos de username y password del formulario estándar de OAuth2.
    El rol se asigna por defecto como USER.
    
    Campos:
      - username: str (obligatorio)
      - password: str (obligatorio)
    
    Respuesta: UserRead con el usuario creado (must_change_password=true por defecto)
    """
    logger.info(f"🔐 Intento de login: username={form_data.username}")
    
    user = await authenticate(form_data.username, form_data.password)
    if not user:
        logger.error(f"❌ Login fallido para: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales inválidas"
        )
    
    token = create_access_token(subject=user.username)
    logger.info(f"✅ Token creado para {user.username}: {token[:50]}...")
    
    return Token(access_token=token, must_change_password=user.must_change_password)

@router.post("/login", response_model=Token)
async def login(payload: LoginRequest):
    user = await authenticate(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    access_token = create_access_token(subject=user.username)
    return Token(access_token=access_token, must_change_password=user.must_change_password)


# ----------------- LOGIN (FORM) -----------------
@router.post("/login/form", response_model=Token, status_code=200, tags=["auth"])
async def login_form_endpoint(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Autenticación con Form-Data (compatible con el botón 'Authorize' de Swagger).
    Campos:
      - username
      - password
    """
    user = await authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token(subject=user.username)
    return Token(access_token=token, must_change_password=user.must_change_password)


# ---------------
@router.post("/anonymous-token", response_model=dict)
async def get_anonymous_token(request: "Request"):
    """
    Token temporal anónimo para formulario público de reservas.
    Vigencia: 1 hora. Vinculado a IP del cliente.
    """
    client_ip = request.client.host
    token = create_access_token(
        subject="anonymous",
        expires_minutes=60,
        extra_claims={"type": "external", "ip": client_ip}
    )
    return {"access_token": token, "expires_in": 3600}
