"""
Schemas para el sistema de lottery de parqueaderos.

Contiene los esquemas de request/response para:
- Configuración del lottery
- Rondas de lottery
- Participantes
"""
from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from propiedad_horizontal.app.domain.enums import LotteryStatus, LotteryParticipantStatus


# ==================== Configuración ====================

class LotteryConfigBase(BaseModel):
    """Base schema para configuración de lottery"""
    weight_propietario: Decimal = Field(
        default=2.0,
        description="Peso adicional para residentes propietarios"
    )
    weight_good_social_behavior: Decimal = Field(
        default=1.5,
        description="Peso adicional para residentes sin llamados de atención"
    )
    weight_payment_compliance: Decimal = Field(
        default=2.0,
        description="Peso adicional para residentes al día en pagos"
    )
    max_consecutive_months: int = Field(
        default=6,
        description="Máximo de meses consecutivos con parqueadero"
    )
    exclusion_draws: int = Field(
        default=2,
        description="Sorteos a esperar después de 6 meses consecutivos"
    )
    assignment_duration_months: int = Field(
        default=1,
        description="Duración de cada asignación en meses"
    )
    propiedad_horizontal_id: Optional[int] = Field(
        default=None,
        description="ID de la propiedad horizontal (null = global)"
    )
    is_active: bool = Field(default=True)


class LotteryConfigCreate(LotteryConfigBase):
    """Schema para crear configuración"""
    pass


class LotteryConfigUpdate(BaseModel):
    """Schema para actualizar configuración"""
    weight_propietario: Optional[Decimal] = None
    weight_good_social_behavior: Optional[Decimal] = None
    weight_payment_compliance: Optional[Decimal] = None
    max_consecutive_months: Optional[int] = None
    exclusion_draws: Optional[int] = None
    assignment_duration_months: Optional[int] = None
    is_active: Optional[bool] = None


class LotteryConfigRead(LotteryConfigBase):
    """Schema para leer configuración"""
    id: int
    propiedad_horizontal_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)


# ==================== Rondas de Lottery ====================

class LotteryRoundBase(BaseModel):
    """Base schema para ronda de lottery"""
    round_number: int = Field(description="Número de ronda (año*100 + mes)")
    round_date: date = Field(description="Fecha del sorteo")
    start_date: date = Field(description="Inicio del período de asignación")
    end_date: date = Field(description="Fin del período de asignación")
    notes: Optional[str] = None


class LotteryRoundCreate(LotteryRoundBase):
    """Schema para crear una ronda"""
    config_id: int = Field(description="ID de configuración a usar")
    available_spots: int = Field(default=0, description="Parqueaderos disponibles")


class LotteryRoundUpdate(BaseModel):
    """Schema para actualizar estado de ronda"""
    status: Optional[LotteryStatus] = None
    assigned_spots: Optional[int] = None
    notes: Optional[str] = None


class LotteryRoundRead(LotteryRoundBase):
    """Schema para leer una ronda"""
    id: int
    status: LotteryStatus
    config_id: Optional[int]
    available_spots: int
    assigned_spots: int
    created_at: datetime
    updated_at: datetime
    executed_by_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class LotteryRoundWithParticipants(LotteryRoundRead):
    """Ronda con sus participantes"""
    participants: List["LotteryParticipantRead"] = []

    model_config = ConfigDict(from_attributes=True)


# ==================== Participantes ====================

class LotteryParticipantBase(BaseModel):
    """Base schema para participante"""
    persona_id: int
    user_id: Optional[int] = None


class LotteryParticipantScore(BaseModel):
    """
    Schema para la puntuación calculada del participante.
    Estos campos son calculados por el servicio.
    """
    base_score: Decimal = Field(default=1.0)
    propietario_factor: Decimal = Field(default=1.0)
    social_behavior_factor: Decimal = Field(default=1.0)
    payment_compliance_factor: Decimal = Field(default=1.0)
    final_score: Decimal = Field(default=1.0)


class LotteryParticipantCreate(LotteryParticipantBase):
    """Schema para crear un participante"""
    round_id: int


class LotteryParticipantRead(LotteryParticipantBase):
    """Schema para leer un participante"""
    id: int
    round_id: int
    status: LotteryParticipantStatus
    assigned_spot_id: Optional[int]
    waiting_list_position: Optional[int]
    random_seed: float
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Información de puntuación
    base_score: Decimal
    propietario_factor: Decimal
    social_behavior_factor: Decimal
    payment_compliance_factor: Decimal
    final_score: Decimal

    model_config = ConfigDict(from_attributes=True)


class LotteryParticipantWithPersona(LotteryParticipantRead):
    """Participante con información de la persona"""
    persona_nombre: str = ""
    persona_apellido: str = ""
    is_propietario: bool = False
    is_arrendatario: bool = False

    model_config = ConfigDict(from_attributes=True)


# ==================== Comportamiento del Residente ====================

class ResidentBehaviorBase(BaseModel):
    """Base schema para comportamiento del residente"""
    total_warnings: int = 0
    warnings_leve: int = 0
    warnings_moderado: int = 0
    warnings_grave: int = 0
    months_payment_current: int = 0
    is_payment_compliant: bool = True
    consecutive_months_with_parking: int = 0
    total_months_with_parking: int = 0
    pending_exclusion_draws: int = 0
    neighbor_complaints: int = 0
    incidents: int = 0


class ResidentBehaviorUpdate(BaseModel):
    """Schema para actualizar comportamiento"""
    total_warnings: Optional[int] = None
    warnings_leve: Optional[int] = None
    warnings_moderado: Optional[int] = None
    warnings_grave: Optional[int] = None
    months_payment_current: Optional[int] = None
    is_payment_compliant: Optional[bool] = None
    consecutive_months_with_parking: Optional[int] = None
    total_months_with_parking: Optional[int] = None
    pending_exclusion_draws: Optional[int] = None
    neighbor_complaints: Optional[int] = None
    incidents: Optional[int] = None


class ResidentBehaviorRead(ResidentBehaviorBase):
    """Schema para leer comportamiento"""
    id: int
    persona_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== Resultados del Sorteo ====================

class LotteryResultItem(BaseModel):
    """Resultado individual del sorteo"""
    position: int
    persona_id: int
    persona_nombre: str
    persona_apellido: str
    status: LotteryParticipantStatus
    final_score: Decimal
    assigned_spot_id: Optional[int] = None
    waiting_list_position: Optional[int] = None


class LotteryResult(BaseModel):
    """Resultado completo del sorteo"""
    round_id: int
    round_number: int
    status: LotteryStatus
    total_participants: int
    selected_count: int
    waiting_list_count: int
    results: List[LotteryResultItem]


# ==================== Ejecución del Lottery ====================

class LotteryExecuteRequest(BaseModel):
    """Request para ejecutar un lottery"""
    config_id: int = Field(description="ID de configuración a usar")
    month: int = Field(ge=1, le=12, description="Mes del lottery")
    year: int = Field(description="Año del lottery")
    available_spots: int = Field(ge=0, description="Número de parqueaderos disponibles")
    notes: Optional[str] = None


class LotteryExecuteResponse(BaseModel):
    """Response después de ejecutar el lottery"""
    round: LotteryRoundRead
    results: LotteryResult
    message: str


# Actualizar referencias Forward
LotteryRoundWithParticipants.model_rebuild()
