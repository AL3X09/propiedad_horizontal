from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from propiedad_horizontal.app.schemas.domain_config import DomainConfigCreate, DomainConfigRead, DomainConfigUpdate
from propiedad_horizontal.app.services import domain_config_service as service
from propiedad_horizontal.app.core.auth import require_permissions

router = APIRouter(
    prefix="/domain-config",
    tags=["domain-config"],
    dependencies=[Depends(require_permissions(["dominio:read"]))]
)

@router.get("", response_model=List[DomainConfigRead])
async def list_configs(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    return await service.list_configs(limit=limit, offset=offset)

@router.get("/{config_id}", response_model=DomainConfigRead)
async def get_config(config_id: int):
    config = await service.get_by_id(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    return config

@router.post("", response_model=DomainConfigRead, status_code=201, dependencies=[Depends(require_permissions(["parking:lottery:write"]))])
async def create_config(payload: DomainConfigCreate):
    return await service.create(domain=payload.domain, is_active=payload.is_active)

@router.patch("/{config_id}", response_model=DomainConfigRead, dependencies=[Depends(require_permissions(["parking:lottery:write"]))])
async def update_config(config_id: int, payload: DomainConfigUpdate):
    config = await service.update(config_id, **payload.model_dump(exclude_unset=True))
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    return config