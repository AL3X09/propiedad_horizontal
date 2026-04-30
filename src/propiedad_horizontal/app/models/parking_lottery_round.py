"""
Modelo de ronda/sorteo de parqueaderos.

Representa cada sesión de sorteo de parqueaderos, que se ejecuta mensualmente.
"""
from tortoise import fields, models
from propiedad_horizontal.app.domain.enums import LotteryStatus


class LotteryRound(models.Model):
    """
    Representa una ronda de sorteo de parqueaderos.
    
    Cada mes se crea una nueva ronda que selecciona los residentes winners
    para los parqueaderos disponibles.
    """
    id = fields.IntField(pk=True)
    
    # Identificación de la ronda
    round_number = fields.IntField(
        description="Número secuencial de la ronda (año*100 + mes)"
    )
    round_date = fields.DateField(
        description="Fecha en que se ejecutó el sorteo"
    )
    
    # Período de la asignación
    start_date = fields.DateField(
        description="Fecha de inicio del período de asignación"
    )
    end_date = fields.DateField(
        description="Fecha de fin del período de asignación"
    )
    
    # Estado del sorteo
    status = fields.CharEnumField(
        LotteryStatus, 
        default=LotteryStatus.PENDING,
        description="Estado actual del sorteo"
    )
    
    # Configuración usada
    config = fields.ForeignKeyField(
        "models.LotteryConfig",
        related_name="rounds",
        null=True,
        on_delete=fields.SET_NULL,
        description="Configuración usada para este sorteo"
    )
    
    # Parqueaderos disponibles
    available_spots = fields.IntField(
        default=0,
        description="Número de parqueaderos disponibles en este sorteo"
    )
    
    # Parqueaderos asignados
    assigned_spots = fields.IntField(
        default=0,
        description="Número de parqueaderos asignados en este sorteo"
    )
    
    # Notas adicionales
    notes = fields.TextField(
        null=True,
        description="Notas adicionales del administrador"
    )
    
    # --- Metadatos ---
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    executed_by = fields.ForeignKeyField(
        "models.User",
        related_name="lottery_rounds_executed",
        null=True,
        on_delete=fields.SET_NULL,
    )

    class Meta:
        table = "parking_lottery_rounds"
        indexes = [("round_date", "status"), ("config_id",)]
        unique_together = [("round_number", "config")]

    def __str__(self) -> str:
        return f"<LotteryRound id={self.id} round={self.round_number} status={self.status}>"
