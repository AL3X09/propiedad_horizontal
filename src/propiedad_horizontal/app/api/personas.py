from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from propiedad_horizontal.app.schemas.persona import PersonaCreate, PersonaUpdate, PersonaRead
from propiedad_horizontal.app.services.persona_service import (
    create_persona, list_personas, get_persona, update_persona, deactivate_persona
)
from propiedad_horizontal.app.core.auth import require_permissions, get_current_user
from propiedad_horizontal.app.models.user import User

router = APIRouter(prefix="/personas", tags=["personas"])

@router.get("/me", response_model=PersonaRead)
async def get_my_persona(current_user: User = Depends(get_current_user)):
    """Obtiene la persona asociada al usuario actual"""
    items = await list_personas(
        usuario_id=current_user.id,
        active_only=False,
        limit=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="No tienes una persona asociada")
    return PersonaRead.model_validate(items[0])

@router.patch("/me", response_model=PersonaRead)
async def update_my_persona(payload: PersonaUpdate, current_user: User = Depends(get_current_user)):
    """Actualiza la persona asociada al usuario actual"""
    items = await list_personas(
        usuario_id=current_user.id,
        active_only=False,
        limit=1,
    )
    if not items:
        raise HTTPException(status_code=404, detail="No tienes una persona asociada")
    persona = await update_persona(items[0].id, payload)
    return PersonaRead.model_validate(persona)

@router.get("/", response_model=list[PersonaRead], dependencies=[Depends(require_permissions(["person:read"]))])
async def list_personas_endpoint(
    # CORRECCIÓN: Ahora filtra por link (casa-torre) en lugar de casa/apartamento
    casa_interior_link_id: Optional[int] = None,
    active_only: bool = True,
    is_propietario: Optional[bool] = None,
    is_arrendatario: Optional[bool] = None,
    nombre_like: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    items = await list_personas(
        casa_interior_link_id=casa_interior_link_id,
        active_only=active_only,
        is_propietario=is_propietario,
        is_arrendatario=is_arrendatario,
        nombre_like=nombre_like,
        limit=limit,
        offset=offset,
    )
    return [PersonaRead.model_validate(i) for i in items]

@router.get("/{persona_id}", response_model=PersonaRead, dependencies=[Depends(require_permissions(["person:read"]))])
async def get_persona_endpoint(persona_id: int):
    p = await get_persona(persona_id)
    if not p:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return PersonaRead.model_validate(p)

@router.post("/", response_model=PersonaRead, status_code=201, dependencies=[Depends(require_permissions(["person:write"]))])
async def create_persona_endpoint(payload: PersonaCreate):
    try:
        p = await create_persona(payload)
        return PersonaRead.model_validate(p)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{persona_id}", response_model=PersonaRead, dependencies=[Depends(require_permissions(["person:write"]))])
async def update_persona_endpoint(persona_id: int, payload: PersonaUpdate):
    p = await update_persona(persona_id, payload)
    if not p:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return PersonaRead.model_validate(p)

@router.post("/{persona_id}/deactivate", status_code=204, dependencies=[Depends(require_permissions(["person:write"]))])
async def deactivate_persona_endpoint(persona_id: int):
    ok = await deactivate_persona(persona_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return None
