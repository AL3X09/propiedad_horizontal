"""
Modelo de configuración del sorteo de parqueaderos.

Permite parametrizar desde la base de datos todos los aspectos del sistema de sorteo:
- Pesos para el modelo probabilístico
- Límites de meses consecutivos
- Períodos de exclusión
"""
from tortoise import fields, models


class LotteryConfig(models.Model):
    """
    Configuración global del sistema de sorteo de parqueaderos.
    
    Todos los parámetros son editables desde la base de datos para permitir
    ajustes sin modificar código.
    """
    id = fields.IntField(pk=True)
    
    # --- Parámetros del modelo probabilístico ---
    # Peso base para propietarios vs arrendatarios
    # Mayor valor = más probabilidad para propietarios
    weight_propietario = fields.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=2.0,
        description="Peso adicional para residentes propietarios (vs arrendatarios)"
    )
    
    # Peso por buen comportamiento social (sin llamados de atención)
    weight_good_social_behavior = fields.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=1.5,
        description="Peso adicional para residentes sin llamados de atención"
    )
    
    # Peso por cumplimiento en pagos
    weight_payment_compliance = fields.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=2.0,
        description="Peso adicional para residentes al día en pagos"
    )
    
    # --- Parámetros de exclusión ---
    # Máximo de meses consecutivos con parqueadero antes de exclusión
    max_consecutive_months = fields.IntField(
        default=6,
        description="Máximo de meses consecutivos con parqueadero antes de exclusión"
    )
    
    # Número de sorteos que debe esperar el excluido
    exclusion_draws = fields.IntField(
        default=2,
        description="Número de sorteos que el residente debe esperar antes de participar de nuevo"
    )
    
    # --- Parámetros de rotación ---
    # Meses de duración de cada asignación
    assignment_duration_months = fields.IntField(
        default=1,
        description="Duración en meses de cada asignación de parqueadero"
    )
    
    # --- Configuración de propiedades horizontales ---
    # FK opcional para configurar por PH específica
    propiedad_horizontal = fields.ForeignKeyField(
        "models.PropiedadHorizontal",
        related_name="lottery_configs",
        null=True,
        on_delete=fields.SET_NULL,
        description="Propiedad horizontal a la que aplica esta configuración"
    )
    
    # Flags de activación
    is_active = fields.BooleanField(
        default=True,
        description="Indica si el sistema de lottery está activo"
    )
    
    # --- Metadatos ---
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    created_by = fields.ForeignKeyField(
        "models.User",
        related_name="lottery_configs_created",
        null=True,
        on_delete=fields.SET_NULL,
    )

    class Meta:
        table = "parking_lottery_config"
        indexes = [("propiedad_horizontal_id", "is_active")]

    def __str__(self) -> str:
        return f"<LotteryConfig id={self.id} ph={self.propiedad_horizontal_id} active={self.is_active}>"
