from tortoise import fields, models


class Trasteo(models.Model):
    """Modelo para registrar trasteos (traslados/movimientos) de bienes de un usuario"""
    id = fields.IntField(pk=True)

    # Usuario propietario del trasteo
    usuario = fields.ForeignKeyField(
        "models.User",
        related_name="trasteos",
        on_delete=fields.CASCADE,
    )

    # Fechas
    fecha_ingreso = fields.DatetimeField()
    fecha_salida = fields.DatetimeField(null=True)

    # Estados
    is_autorizado = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)

    # Auditoría
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "trasteos"
        indexes = [
            ("usuario_id", "is_active"),
            ("fecha_ingreso", "fecha_salida"),
            ("is_autorizado",),
        ]

    def __str__(self) -> str:
        return f"<Trasteo {self.id} Usuario:{self.usuario_id} Autorizado:{self.is_autorizado} {'active' if self.is_active else 'inactive'}>"
