"""
Rutas API para el sistema de lottery de parqueaderos.

Endpoints disponibles:
- Configuración del lottery
- Ejecución de sorteos
- Consulta de resultados
- Gestión de comportamiento de residentes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date

from propiedad_horizontal.app.schemas.parking_lottery import (
    LotteryConfigCreate,
    LotteryConfigUpdate,
    LotteryConfigRead,
    LotteryRoundCreate,
    LotteryRoundUpdate,
    LotteryRoundRead,
    LotteryParticipantRead,
    LotteryResult,
    LotteryExecuteRequest,
    LotteryExecuteResponse,
    ResidentBehaviorUpdate,
    ResidentBehaviorRead,
    LotteryParticipantScore,
)

from propiedad_horizontal.app.services import parking_lottery_service as service
from propiedad_horizontal.app.core.auth import require_permissions


router = APIRouter(
    prefix="/parking/lottery",
    tags=["parking-lottery"],
    dependencies=[Depends(require_permissions(["parking:lottery:read"]))]
)


# ==================== Configuración ====================

@router.get("/configs", response_model=List[LotteryConfigRead])
async def list_configs(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Lista todas las configuraciones de lottery"""
    configs = await service.list_configs(limit=limit, offset=offset)
    return configs


@router.get("/configs/{config_id}", response_model=LotteryConfigRead)
async def get_config(config_id: int):
    """Obtiene una configuración por ID"""
    from propiedad_horizontal.app.models.parking_lottery_config import LotteryConfig
    config = await LotteryConfig.get_or_none(id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    return config


@router.post("/configs", response_model=LotteryConfigRead, status_code=201, dependencies=[Depends(require_permissions(["parking:lottery:write"]))])
async def create_config(
    payload: LotteryConfigCreate,
):
    """Crea una nueva configuración de lottery"""
    config = await service.create_config(
        weight_propietario=payload.weight_propietario,
        weight_good_social_behavior=payload.weight_good_social_behavior,
        weight_payment_compliance=payload.weight_payment_compliance,
        max_consecutive_months=payload.max_consecutive_months,
        exclusion_draws=payload.exclusion_draws,
        assignment_duration_months=payload.assignment_duration_months,
        propiedad_horizontal_id=payload.propiedad_horizontal_id,
    )
    return config


@router.patch("/configs/{config_id}", response_model=LotteryConfigRead, dependencies=[Depends(require_permissions(["parking:lottery:write"]))])
async def update_config(
    config_id: int,
    payload: LotteryConfigUpdate,
):
    """Actualiza una configuración existente"""
    update_data = payload.model_dump(exclude_unset=True)
    config = await service.update_config(config_id, **update_data)
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    return config


# ==================== Rondas ====================

@router.get("/rounds", response_model=List[LotteryRoundRead])
async def list_rounds(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Lista todas las rondas de lottery"""
    rounds = await service.get_rounds(limit=limit, offset=offset)
    return rounds


@router.get("/rounds/{round_id}", response_model=LotteryRoundRead)
async def get_round(round_id: int):
    """Obtiene una ronda por ID"""
    round_obj = await service.get_round(round_id)
    if not round_obj:
        raise HTTPException(status_code=404, detail="Ronda no encontrada")
    return round_obj


@router.get("/rounds/{round_id}/results", response_model=LotteryResult)
async def get_round_results(round_id: int):
    """Obtiene los resultados de una ronda"""
    results = await service.get_round_results(round_id)
    if not results:
        raise HTTPException(status_code=404, detail="Ronda no encontrada")
    return results


@router.get("/rounds/{round_id}/participants", response_model=List[LotteryParticipantRead])
async def get_round_participants(round_id: int):
    """Obtiene los participantes de una ronda"""
    round_obj = await service.get_round(round_id)
    if not round_obj:
        raise HTTPException(status_code=404, detail="Ronda no encontrada")
    
    participants = await service.get_participants_by_round(round_id)
    return participants


# ==================== Ejecución del Lottery ====================

@router.post("/execute", response_model=LotteryExecuteResponse, dependencies=[Depends(require_permissions(["parking:lottery:execute"]))])
async def execute_lottery(
    payload: LotteryExecuteRequest,
):
    """
    Ejecuta un nuevo sorteo de parqueaderos.
    
    Este endpoint:
    1. Valida la configuración
    2. Obtiene residentes elegibles
    3. Calcula puntuaciones probabilísticas
    4. Ejecuta el sorteo
    5. Actualiza el historial de comportamiento
    """
    try:
        lottery_round, participants = await service.execute_lottery(
            config_id=payload.config_id,
            month=payload.month,
            year=payload.year,
            available_spots=payload.available_spots,
            notes=payload.notes,
        )
        
        results = await service.get_round_results(lottery_round.id)
        
        return LotteryExecuteResponse(
            round=lottery_round,
            results=results,
            message=f"Sorteo ejecutado exitosamente. {results['selected_count']} parqueaderos asignados."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Comportamiento de Residentes ====================

@router.get("/residents/{persona_id}/behavior", response_model=ResidentBehaviorRead)
async def get_resident_behavior(persona_id: int):
    """Obtiene el registro de comportamiento de un residente"""
    behavior = await service.get_or_create_behavior(persona_id)
    return behavior


@router.patch("/residents/{persona_id}/behavior", response_model=ResidentBehaviorRead, dependencies=[Depends(require_permissions(["parking:lottery:write"]))])
async def update_resident_behavior(
    persona_id: int,
    payload: ResidentBehaviorUpdate,
):
    """Actualiza el comportamiento de un residente"""
    update_data = payload.model_dump(exclude_unset=True)
    behavior = await service.update_behavior(persona_id, **update_data)
    if not behavior:
        raise HTTPException(status_code=404, detail="Residente no encontrado")
    return behavior


@router.post("/residents/{persona_id}/warning", dependencies=[Depends(require_permissions(["parking:lottery:write"]))])
async def add_warning(
    persona_id: int,
    warning_type: str = Query(..., description="Tipo: leve, moderado, grave"),
    description: str = Query(..., description="Descripción del llamado"),
    incident_date: date = Query(..., description="Fecha del incidente"),
):
    """Registra un nuevo llamado de atención a un residente"""
    if warning_type not in ["leve", "moderado", "grave"]:
        raise HTTPException(status_code=400, detail="Tipo de llamado inválido")
    
    warning = await service.add_warning(
        persona_id=persona_id,
        warning_type=warning_type,
        description=description,
        incident_date=incident_date,
    )
    return {"message": "Llamado de atención registrado", "warning_id": warning.id}


@router.patch("/residents/{persona_id}/payment-status", dependencies=[Depends(require_permissions(["parking:lottery:write"]))])
async def update_payment_status(
    persona_id: int,
    is_compliant: bool = Query(..., description="True si está al día, False si no"),
):
    """Actualiza el estado de pago de un residente"""
    behavior = await service.update_payment_status(persona_id, is_compliant)
    if not behavior:
        raise HTTPException(status_code=404, detail="Residente no encontrado")
    
    status_text = "al día" if is_compliant else "moroso"
    return {"message": f"Estado de pago actualizado: {status_text}"}


# ==================== Verificación de Elegibilidad ====================

@router.get("/residents/{persona_id}/eligibility")
async def check_eligibility(
    persona_id: int,
    config_id: Optional[int] = Query(None, description="ID de configuración (opcional)")
):
    """
    Verifica si un residente es elegible para el lottery.
    
    Returns:
        - eligible: true/false
        - reason: razón de la elegibilidad o exclusión
        - scores: puntuación actual (si es elegible)
    """
    from propiedad_horizontal.app.models.persona import Persona
    
    persona = await Persona.get_or_none(id=persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Residente no encontrado")
    
    # Obtener config
    if config_id:
        from propiedad_horizontal.app.models.parking_lottery_config import LotteryConfig
        config = await LotteryConfig.get_or_none(id=config_id)
    else:
        config = await service.get_active_config()
    
    if not config:
        raise HTTPException(status_code=400, detail="No hay configuración de lottery activa")
    
    # Verificar elegibilidad
    is_eligible, reason = await service.check_eligibility(persona_id, config)
    
    result = {
        "persona_id": persona_id,
        "eligible": is_eligible,
        "reason": reason
    }
    
    # Si es elegible, devolver puntuación
    if is_eligible:
        behavior = await service.get_or_create_behavior(persona_id)
        scores = await service.calculate_participant_score(persona, behavior, config)
        result["scores"] = scores
    
    return result
