from tortoise import fields, models

class TrasteoBien(models.Model):
    """Modelo intermedio para asociar bienes a trasteos con cantidad"""
    id = fields.IntField(pk=True)

    # Referencias
    trasteo = fields.ForeignKeyField(
        "models.Trasteo",
        related_name="bienes",
        on_delete=fields.CASCADE,
    )

    bien = fields.ForeignKeyField(
        "models.Bien",
        related_name="trasteos",
        on_delete=fields.CASCADE,
    )

    # Cantidad del bien en este trasteo
    cantidad = fields.IntField(default=1)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "trasteo_bienes"
        unique_together = (("trasteo", "bien"),)  # Un bien no puede repetirse en un mismo trasteo
        indexes = [
            ("trasteo_id",),
            ("bien_id",),
        ]

    def __str__(self) -> str:
        return f"<TrasteoBien Trasteo:{self.trasteo_id} Bien:{self.bien_id} Cantidad:{self.cantidad}>"
