from tortoise import fields, models
from propiedad_horizontal.app.domain.enums import ApartmentStatus

class CasaApartamentoInteriorTorre(models.Model):
    id = fields.IntField(pk=True)

    torre_interior = fields.ForeignKeyField(
        "models.TorreInterior",
        related_name="links_casas",
        on_delete=fields.CASCADE,
    )
    # FKs a ambos lados de la relación
    casa_apartamento = fields.ForeignKeyField(
        "models.CasaApartamento",
        related_name="links_interiores",
        on_delete=fields.CASCADE,
    )

    # Campos adicionales solicitados
    status = fields.CharEnumField(ApartmentStatus, default=ApartmentStatus.DESHABITADO)
    num_habitaciones = fields.IntField(null=False, default=2)

    # Soft delete / trazabilidad
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "ph_casa_interior_links"
        # Evita duplicados exactos del par (casa, interior)
        unique_together = (("casa_apartamento_id", "torre_interior_id"),)
        indexes = [
            ("casa_apartamento_id", "torre_interior_id"),
            ("status",),
            ("is_active",),
        ]

    def __str__(self) -> str:
        return f"<CasaInteriorLink {self.id} CA:{self.casa_apartamento_id} TI:{self.torre_interior_id} {self.status} {self.num_habitaciones}>"
