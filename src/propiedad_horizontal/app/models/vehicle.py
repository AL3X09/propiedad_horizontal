from tortoise import fields, models


class Vehicle(models.Model):
    """
    Modelo para gestionar los vehículos de las personas.
    Cada vehículo pertenece a una persona y tiene un tipo de vehículo asociado.
    """
    id = fields.IntField(pk=True)

    persona = fields.ForeignKeyField(
        "models.Persona",
        related_name="vehicles",
        on_delete=fields.CASCADE,
    )

    vehicle_type = fields.ForeignKeyField(
        "models.VehicleType",
        related_name="vehicles",
        on_delete=fields.CASCADE,
    )

    placa_code = fields.CharField(max_length=20, unique=True, index=True)

    is_active = fields.BooleanField(default=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "vehicles"
        indexes = [
            ("persona_id", "is_active"),
            ("vehicle_type_id", "is_active"),
        ]

    def __str__(self) -> str:
        return f"<Vehicle {self.id} {self.placa_code} Persona:{self.persona_id} {'active' if self.is_active else 'inactive'}>"