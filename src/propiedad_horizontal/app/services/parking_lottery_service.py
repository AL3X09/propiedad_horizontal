"""
Servicio de lottery de parqueaderos.

Este módulo implementa el modelo probabilístico para la asignación de parqueaderos:
1. Propietario tiene más probabilidad que arrendatario
2. Residente sin llamados de atención tiene más probabilidad
3. Residente con buen comportamiento social tiene más probabilidad
4. Residente al día en pagos tiene más probabilidad

El sistema rota mensualmente y excluye a residentes que han tenido
parqueadero por 6 meses consecutivos durante 2 sorteos.
"""
import random
import math
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from propiedad_horizontal.app.models.parking_lottery_config import LotteryConfig
from propiedad_horizontal.app.models.parking_lottery_round import LotteryRound
from propiedad_horizontal.app.models.parking_lottery_participant import LotteryParticipant
from propiedad_horizontal.app.models.resident_behavior import ResidentBehavior, WarningRecord
from propiedad_horizontal.app.models.persona import Persona
from propiedad_horizontal.app.models.parking import ParkingSpot
from propiedad_horizontal.app.models.parking_assignment import MonthlyAssignment
from propiedad_horizontal.app.models.user import User
from propiedad_horizontal.app.models.vehicle_type import VehicleType

from propiedad_horizontal.app.domain.enums import LotteryStatus, LotteryParticipantStatus, AssignmentStatus


# ==================== Helper Functions ====================

def _add_months(start: date, months: int) -> date:
    """Suma meses a una fecha"""
    from calendar import monthrange
    y = start.year + (start.month - 1 + months) // 12
    m = (start.month - 1 + months) % 12 + 1
    d = start.day
    last_day = monthrange(y, m)[1]
    if d > last_day:
        d = last_day
    return date(y, m, d)


def _get_round_number(year: int, month: int) -> int:
    """Calcula el número de ronda (año*100 + mes)"""
    return year * 100 + month


async def _create_monthly_assignment_from_lottery(
    participant: LotteryParticipant,
    spot: ParkingSpot,
    start_date: date,
    config: LotteryConfig,
) -> MonthlyAssignment:
    """
    Crea un MonthlyAssignment a partir de un participante seleccionado del lottery.
    """
    # Calcular end_date
    end_date = _add_months(start_date, config.assignment_duration_months)
    
    # Obtener precio del spot - convertir de string a Decimal para cálculo, luego a string para almacenar
    monthly_price_decimal = Decimal(spot.monthly_price) if spot.monthly_price else Decimal("0")
    total_price_decimal = monthly_price_decimal * config.assignment_duration_months
    # Convertir a string para almacenar en CharField del modelo
    monthly_price_str = str(monthly_price_decimal)
    total_price_str = str(total_price_decimal)
    
    # Obtener tipo de vehículo - por defecto usamos CARRO (id=1)
    vehicle_type_id = 1
    
    # Crear la asignación (sin vehicle_code porque el modelo no lo tiene)
    assignment = await MonthlyAssignment.create(
        spot_id=spot.id,
        persona_id=participant.persona_id,
        start_date=start_date,
        months=config.assignment_duration_months,
        end_date=end_date,
        vehicle_type_id=vehicle_type_id,
        # vehicle_code eliminado: el modelo MonthlyAssignment no tiene este campo
        status=AssignmentStatus.ACTIVE,
        monthly_price=monthly_price_str,
        total_price=total_price_str,
    )
    
    return assignment


# ==================== Configuración ====================

async def get_active_config(propiedad_horizontal_id: Optional[int] = None) -> Optional[LotteryConfig]:
    """
    Obtiene la configuración activa del lottery.
    
    Busca primero una configuración específica para la PH, 
    si no existe usa la global.
    """
    # Primero buscar configuración específica de PH
    if propiedad_horizontal_id:
        config = await LotteryConfig.filter(
            propiedad_horizontal_id=propiedad_horizontal_id,
            is_active=True
        ).first()
        if config:
            return config
    
    # Buscar configuración global
    config = await LotteryConfig.filter(
        propiedad_horizontal_id__isnull=True,
        is_active=True
    ).first()
    
    return config


async def create_config(
    weight_propietario: Decimal,
    weight_good_social_behavior: Decimal,
    weight_payment_compliance: Decimal,
    max_consecutive_months: int,
    exclusion_draws: int,
    assignment_duration_months: int,
    propiedad_horizontal_id: Optional[int] = None,
    created_by_id: Optional[int] = None
) -> LotteryConfig:
    """Crea una nueva configuración de lottery"""
    config = await LotteryConfig.create(
        weight_propietario=weight_propietario,
        weight_good_social_behavior=weight_good_social_behavior,
        weight_payment_compliance=weight_payment_compliance,
        max_consecutive_months=max_consecutive_months,
        exclusion_draws=exclusion_draws,
        assignment_duration_months=assignment_duration_months,
        propiedad_horizontal_id=propiedad_horizontal_id,
        created_by_id=created_by_id,
        is_active=True
    )
    return config


async def update_config(config_id: int, **kwargs) -> Optional[LotteryConfig]:
    """Actualiza una configuración existente"""
    config = await LotteryConfig.get_or_none(id=config_id)
    if not config:
        return None
    
    for key, value in kwargs.items():
        if value is not None and hasattr(config, key):
            setattr(config, key, value)
    
    await config.save()
    return config


async def list_configs(limit: int = 100, offset: int = 0) -> List[LotteryConfig]:
    """Lista todas las configuraciones"""
    return await LotteryConfig.all().offset(offset).limit(limit).order_by("-created_at")


# ==================== Residentes y Comportamiento ====================

async def get_or_create_behavior(persona_id: int) -> ResidentBehavior:
    """Obtiene o crea el registro de comportamiento de un residente"""
    behavior = await ResidentBehavior.get_or_none(persona_id=persona_id)
    if not behavior:
        behavior = await ResidentBehavior.create(persona_id=persona_id)
    return behavior


async def update_behavior(persona_id: int, **kwargs) -> Optional[ResidentBehavior]:
    """Actualiza el comportamiento de un residente"""
    behavior = await get_or_create_behavior(persona_id)
    
    for key, value in kwargs.items():
        if value is not None and hasattr(behavior, key):
            setattr(behavior, key, value)
    
    await behavior.save()
    return behavior


async def check_eligibility(persona_id: int, config: LotteryConfig) -> Tuple[bool, str]:
    """
    Verifica si un residente es elegible para participar.
    
    Returns:
        (es_eligible, razon)
    """
    behavior = await get_or_create_behavior(persona_id)
    
    # Verificar exclusión temporal
    if behavior.pending_exclusion_draws > 0:
        return False, f"Excluido temporalmente. Debe esperar {behavior.pending_exclusion_draws} sorteos"
    
    # Verificar meses consecutivos con parqueadero
    if behavior.consecutive_months_with_parking >= config.max_consecutive_months:
        return False, f"Ha alcanzado el máximo de {config.max_consecutive_months} meses consecutivos"
    
    return True, "Elegible"


# ==================== Cálculo de Puntuación Probabilística ====================

async def calculate_participant_score(
    persona: Persona,
    behavior: ResidentBehavior,
    config: LotteryConfig
) -> dict:
    """
    Calcula la puntuación probabilística de un participante.
    
    Modelo matemático:
    - Score base = 1.0
    - Propietario: multiplica por weight_propietario
    - Sin advertencias: multiplica por weight_good_social_behavior  
    - Al día en pagos: multiplica por weight_payment_compliance
    
    La puntuación final es el producto de todos los factores.
    """
    # Factor base
    base_score = Decimal("1.0")
    
    # Factor de propietario vs arrendatario
    if persona.is_propietario and not persona.is_arrendatario:
        propietario_factor = config.weight_propietario
    elif persona.is_arrendatario:
        propietario_factor = Decimal("1.0")
    else:
        propietario_factor = Decimal("1.0")
    
    # Factor de comportamiento social (sin advertencias = bonus)
    if behavior.total_warnings == 0:
        social_behavior_factor = config.weight_good_social_behavior
    elif behavior.total_warnings <= 2:
        social_behavior_factor = Decimal("1.0")
    else:
        # Reducir probabilidad si tiene muchas advertencias
        social_behavior_factor = max(Decimal("0.5"), Decimal("1.0") - Decimal(behavior.total_warnings * 0.1))
    
    # Factor de cumplimiento de pagos
    if behavior.is_payment_compliant:
        payment_compliance_factor = config.weight_payment_compliance
    else:
        payment_compliance_factor = Decimal("0.3")  # Gran penalización
    
    # Calcular puntuación final
    final_score = base_score * propietario_factor * social_behavior_factor * payment_compliance_factor
    
    return {
        "base_score": base_score,
        "propietario_factor": propietario_factor,
        "social_behavior_factor": social_behavior_factor,
        "payment_compliance_factor": payment_compliance_factor,
        "final_score": final_score
    }


# ==================== Ejecución del Lottery ====================

async def execute_lottery(
    config_id: int,
    month: int,
    year: int,
    available_spots: int,
    executed_by_id: Optional[int] = None,
    notes: Optional[str] = None
) -> Tuple[LotteryRound, List[LotteryParticipant]]:
    """
    Ejecuta el proceso completo de lottery:
    1. Valida la configuración
    2. Obtiene residentes elegibles
    3. Calcula puntuaciones
    4. Ejecuta el sorteo ponderado
    5. Actualiza el historial de comportamiento
    """
    # Obtener configuración
    config = await LotteryConfig.get_or_none(id=config_id)
    if not config:
        raise ValueError("Configuración de lottery no encontrada")
    
    if not config.is_active:
        raise ValueError("La configuración de lottery está desactivada")
    
    # Verificar que no exista una ronda para ese mes
    round_number = _get_round_number(year, month)
    existing = await LotteryRound.filter(
        round_number=round_number,
        config_id=config_id
    ).first()
    if existing:
        raise ValueError(f"Ya existe una ronda de lottery para {month}/{year}")
    
    # Calcular fechas del período
    round_date = date.today()
    start_date = date(year, month, 1)
    end_date = _add_months(start_date, config.assignment_duration_months) - timedelta(days=1)
    
    # Crear la ronda
    lottery_round = await LotteryRound.create(
        round_number=round_number,
        round_date=round_date,
        start_date=start_date,
        end_date=end_date,
        status=LotteryStatus.IN_PROGRESS,
        config_id=config_id,
        available_spots=available_spots,
        notes=notes,
        executed_by_id=executed_by_id
    )
    
    # Obtener todos los residentes activos
    residentes = await Persona.filter(
        is_active=True
    ).prefetch_related("usuario")
    
    # Procesar participantes
    participants = []
    for persona in residentes:
        # Verificar elegibilidad
        is_eligible, _ = await check_eligibility(persona.id, config)
        
        if not is_eligible:
            # Crear registro de participante excluido
            participant = await LotteryParticipant.create(
                round_id=lottery_round.id,
                persona_id=persona.id,
                user_id=persona.usuario_id if hasattr(persona, 'usuario_id') else None,
                status=LotteryParticipantStatus.EXCLUDED_THIS_ROUND,
                random_seed=random.random()
            )
            participants.append(participant)
            continue
        
        # Obtener comportamiento
        behavior = await get_or_create_behavior(persona.id)
        
        # Calcular puntuación
        scores = await calculate_participant_score(persona, behavior, config)
        
        # Crear participante
        participant = await LotteryParticipant.create(
            round_id=lottery_round.id,
            persona_id=persona.id,
            user_id=persona.usuario_id if hasattr(persona, 'usuario_id') else None,
            status=LotteryParticipantStatus.ELIGIBLE,
            base_score=scores["base_score"],
            propietario_factor=scores["propietario_factor"],
            social_behavior_factor=scores["social_behavior_factor"],
            payment_compliance_factor=scores["payment_compliance_factor"],
            final_score=scores["final_score"],
            random_seed=random.random()
        )
        participants.append(participant)
    
    # Ordenar participantes por puntuación (mayor a menor) y usar random_seed para desempates
    eligible_participants = [p for p in participants if p.status == LotteryParticipantStatus.ELIGIBLE]
    eligible_participants.sort(key=lambda p: (p.final_score, p.random_seed), reverse=True)
    
    # Obtener parqueaderos disponibles
    available_parking_spots = await ParkingSpot.filter(
        is_active=True
    ).limit(available_spots)
    
    # Asignar parqueaderos a los primeros N participantes
    assigned_count = 0
    for i, participant in enumerate(eligible_participants):
        if assigned_count < len(available_parking_spots):
            # Asignar parqueadero
            participant.status = LotteryParticipantStatus.SELECTED
            participant.assigned_spot_id = available_parking_spots[assigned_count].id
            await participant.save()
            
            # Crear MonthlyAssignment automáticamente
            spot = available_parking_spots[assigned_count]
            try:
                await _create_monthly_assignment_from_lottery(
                    participant=participant,
                    spot=spot,
                    start_date=start_date,
                    config=config,
                )
            except Exception as e:
                # Log error pero no detener el proceso
                print(f"Error creando MonthlyAssignment para participante {participant.id}: {e}")
            
            assigned_count += 1
        else:
            # Lista de espera
            participant.status = LotteryParticipantStatus.NOT_SELECTED
            participant.waiting_list_position = i - assigned_count + 1
            await participant.save()
    
    # Actualizar contadores de meses consecutivos
    for participant in eligible_participants:
        if participant.status == LotteryParticipantStatus.SELECTED:
            behavior = await get_or_create_behavior(participant.persona_id)
            behavior.consecutive_months_with_parking += 1
            behavior.total_months_with_parking += 1
            
            # Si alcanza el máximo, configurar exclusión
            if behavior.consecutive_months_with_parking >= config.max_consecutive_months:
                behavior.pending_exclusion_draws = config.exclusion_draws
                behavior.consecutive_months_with_parking = 0
            
            await behavior.save()
        else:
            # Si no fue seleccionado, reiniciar contador de consecutivos
            behavior = await get_or_create_behavior(participant.persona_id)
            if behavior.consecutive_months_with_parking > 0:
                behavior.consecutive_months_with_parking = 0
                await behavior.save()
    
    # Actualizar sorteos pendientes de exclusión
    all_behaviors = await ResidentBehavior.all()
    for behavior in all_behaviors:
        if behavior.pending_exclusion_draws > 0:
            behavior.pending_exclusion_draws -= 1
            await behavior.save()
    
    # Actualizar estado de la ronda
    lottery_round.status = LotteryStatus.COMPLETED
    lottery_round.assigned_spots = assigned_count
    await lottery_round.save()
    
    return lottery_round, participants


from datetime import timedelta


# ==================== Consultas ====================

async def get_round(round_id: int) -> Optional[LotteryRound]:
    """Obtiene una ronda por ID"""
    return await LotteryRound.get_or_none(id=round_id).prefetch_related("config", "executed_by")


async def get_rounds(limit: int = 100, offset: int = 0) -> List[LotteryRound]:
    """Lista las rondas de lottery"""
    return await LotteryRound.all().select_related("config").offset(offset).limit(limit).order_by("-round_date")


async def get_participants_by_round(round_id: int) -> List[LotteryParticipant]:
    """Obtiene los participantes de una ronda"""
    return await LotteryParticipant.filter(
        round_id=round_id
    ).select_related("persona", "user", "assigned_spot").order_by("-final_score")


async def get_round_results(round_id: int) -> Optional[dict]:
    """Obtiene los resultados completos de una ronda"""
    lottery_round = await get_round(round_id)
    if not lottery_round:
        return None
    
    participants = await get_participants_by_round(round_id)
    
    # Obtener info de personas
    personas_ids = [p.persona_id for p in participants]
    personas = await Persona.filter(id__in=personas_ids)
    personas_map = {p.id: p for p in personas}
    
    results = []
    for p in participants:
        persona = personas_map.get(p.persona_id)
        results.append({
            "position": results.__len__() + 1,
            "persona_id": p.persona_id,
            "persona_nombre": persona.nombres if persona else "",
            "persona_apellido": persona.apellidos if persona else "",
            "status": p.status,
            "final_score": p.final_score,
            "assigned_spot_id": p.assigned_spot_id,
            "waiting_list_position": p.waiting_list_position
        })
    
    selected_count = len([p for p in participants if p.status == LotteryParticipantStatus.SELECTED])
    waiting_list_count = len([p for p in participants if p.status == LotteryParticipantStatus.NOT_SELECTED])
    
    return {
        "round_id": lottery_round.id,
        "round_number": lottery_round.round_number,
        "status": lottery_round.status,
        "total_participants": len(participants),
        "selected_count": selected_count,
        "waiting_list_count": waiting_list_count,
        "results": results
    }


# ==================== Comportamiento ====================

async def add_warning(
    persona_id: int,
    warning_type: str,
    description: str,
    incident_date: date,
    recorded_by_id: Optional[int] = None
) -> WarningRecord:
    """Registra un nuevo llamado de atención"""
    # Crear el registro de warning
    warning = await WarningRecord.create(
        persona_id=persona_id,
        warning_type=warning_type,
        description=description,
        incident_date=incident_date,
        recorded_by_id=recorded_by_id
    )
    
    # Actualizar contadores en ResidentBehavior
    behavior = await get_or_create_behavior(persona_id)
    behavior.total_warnings += 1
    
    if warning_type == "leve":
        behavior.warnings_leve += 1
    elif warning_type == "moderado":
        behavior.warnings_moderado += 1
    elif warning_type == "grave":
        behavior.warnings_grave += 1
    
    await behavior.save()
    
    return warning


async def update_payment_status(persona_id: int, is_compliant: bool) -> Optional[ResidentBehavior]:
    """Actualiza el estado de pago de un residente"""
    return await update_behavior(persona_id, is_payment_compliant=is_compliant)
