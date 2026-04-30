"""
Modelo de participante en el sorteo de parqueaderos.

Representa cada residente que participa en una ronda específica del sorteo.
Incluye su puntuación calculada y el estado de participación.
"""
from tortoise import fields, models
from propiedad_horizontal.app.domain.enums import LotteryParticipantStatus


class LotteryParticipant(models.Model):
    """
    Participante en una ronda específica del sorteo.
    
    Almacena la información del residente, su puntuación calculada
    según el modelo probabilístico, y el resultado del sorteo.
    """
    id = fields.IntField(pk=True)
    
    # Ronda a la que pertenece
    round = fields.ForeignKeyField(
        "models.LotteryRound",
        related_name="participants",
        on_delete=fields.CASCADE,
    )
    
    # Residente participante
    persona = fields.ForeignKeyField(
        "models.Persona",
        related_name="lottery_participations",
        on_delete=fields.CASCADE,
    )
    
    # Usuario asociado (para notificaciones)
    user = fields.ForeignKeyField(
        "models.User",
        related_name="lottery_participations",
        null=True,
        on_delete=fields.SET_NULL,
    )
    
    # Estado del participante
    status = fields.CharEnumField(
        LotteryParticipantStatus,
        default=LotteryParticipantStatus.ELIGIBLE,
    )
    
    # --- Puntuación probabilística ---
    # Puntuación base del participante
    base_score = fields.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=1.0,
        description="Puntuación base del participante"
    )
    
    # Factores adicionales
    propietario_factor = fields.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        description="Factor por ser propietario (1.0 = arrendatario)"
    )
    
    social_behavior_factor = fields.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        description="Factor por buen comportamiento social"
    )
    
    payment_compliance_factor = fields.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        description="Factor por cumplimiento de pagos"
    )
    
    # Puntuación final (producto de todos los factores)
    final_score = fields.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=1.0,
        description="Puntuación final calculada para el sorteo"
    )
    
    # --- Resultados del sorteo ---
    # Parqueadero asignado (si fue winner)
    assigned_spot = fields.ForeignKeyField(
        "models.ParkingSpot",
        related_name="lottery_assignments",
        null=True,
        on_delete=fields.SET_NULL,
    )
    
    # Posición en la lista de espera
    waiting_list_position = fields.IntField(
        null=True,
        description="Posición en lista de espera si no fue seleccionado"
    )
    
    # Número aleatorio para desempates
    random_seed = fields.FloatField(
        description="Semilla aleatoria para desempates"
    )
    
    # Notas
    notes = fields.TextField(
        null=True,
        description="Notas adicionales sobre el participante"
    )
    
    # --- Metadatos ---
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "parking_lottery_participants"
        indexes = [
            ("round_id", "status"),
            ("persona_id", "round_id"),
            ("final_score",),
        ]
        unique_together = [("round_id", "persona_id")]

    def __str__(self) -> str:
        return f"<LotteryParticipant id={self.id} round={self.round_id} persona={self.persona_id} status={self.status}>"
