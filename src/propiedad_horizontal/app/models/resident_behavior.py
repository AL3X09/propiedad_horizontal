"""
Modelo de seguimiento del comportamiento del residente.

Registra los llamados de atención, historial de pagos y otros comportamientos
relevantes para el cálculo de probabilidades en el sorteo de parqueaderos.
"""
from tortoise import fields, models
from enum import Enum


class WarningType(str, Enum):
    """Tipos de llamados de atención"""
    LEVE = "leve"
    MODERADO = "moderado"
    GRAVE = "grave"


class ResidentBehavior(models.Model):
    """
    Registro del comportamiento de cada residente.
    
    Acumula información histórica sobre:
    - Llamados de atención (tipo y cantidad)
    - Historial de pagos
    - Quejas recibidas
    """
    id = fields.IntField(pk=True)
    
    # Residente al que corresponde el registro
    persona = fields.ForeignKeyField(
        "models.Persona",
        related_name="behavior_records",
        on_delete=fields.CASCADE,
    )
    
    # --- Contadores de comportamiento ---
    # Total de llamados de atención
    total_warnings = fields.IntField(
        default=0,
        description="Total de llamados de atención recibidos"
    )
    
    # Llamados de atención leves
    warnings_leve = fields.IntField(
        default=0,
        description="Llamados de atención leves"
    )
    
    # Llamados de atención moderados
    warnings_moderado = fields.IntField(
        default=0,
        description="Llamados de atención moderados"
    )
    
    # Llamados de atención graves
    warnings_grave = fields.IntField(
        default=0,
        description="Llamados de atención graves"
    )
    
    # --- Historial de pagos ---
    # Meses al día en pagos (en los últimos 12 meses)
    months_payment_current = fields.IntField(
        default=0,
        description="Meses al día en pagos (últimos 12 meses)"
    )
    
    # Indicates if resident is currently up to date with payments
    is_payment_compliant = fields.BooleanField(
        default=True,
        description="Indica si el residente está al día en pagos"
    )
    
    # --- Parqueadero ---
    # Meses consecutivos con parqueadero
    consecutive_months_with_parking = fields.IntField(
        default=0,
        description="Meses consecutivos con asignación de parqueadero"
    )
    
    # Total de meses con parqueadero (histórico)
    total_months_with_parking = fields.IntField(
        default=0,
        description="Total de meses con asignación de parqueadero"
    )
    
    # Sorteos excluidos pendientes
    pending_exclusion_draws = fields.IntField(
        default=0,
        description="Número de sorteos que debe esperar antes de participar"
    )
    
    # --- Comportamiento social ---
    # Quejas de vecinos
    neighbor_complaints = fields.IntField(
        default=0,
        description="Número de quejas de vecinos"
    )
    
    # Incidentes registrados
    incidents = fields.IntField(
        default=0,
        description="Número de incidentes registrados"
    )
    
    # --- Metadatos ---
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "resident_behaviors"
        indexes = [("persona_id",)]

    def __str__(self) -> str:
        return f"<ResidentBehavior id={self.id} persona={self.persona_id} warnings={self.total_warnings}>"


class WarningRecord(models.Model):
    """
    Registro individual de cada llamado de atención.
    
    Permite mantener un historial detallado de los comportamientos.
    """
    id = fields.IntField(pk=True)
    
    # Residente
    persona = fields.ForeignKeyField(
        "models.Persona",
        related_name="warning_records",
        on_delete=fields.CASCADE,
    )
    
    # Tipo de llamado
    warning_type = fields.CharEnumField(WarningType)
    
    # Descripción
    description = fields.TextField(
        description="Descripción del llamado de atención"
    )
    
    # Fecha del incidente
    incident_date = fields.DateField()
    
    # Registrado por
    recorded_by = fields.ForeignKeyField(
        "models.User",
        related_name="warnings_recorded",
        null=True,
        on_delete=fields.SET_NULL,
    )
    
    # ¿Está activo? (para soft delete)
    is_active = fields.BooleanField(
        default=True,
        description="Indica si el registro está activo"
    )
    
    # --- Metadatos ---
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "warning_records"
        indexes = [("persona_id", "incident_date"), ("is_active",)]

    def __str__(self) -> str:
        return f"<WarningRecord id={self.id} persona={self.persona_id} type={self.warning_type}>"
