
from tortoise import fields, models

class TorreInterior(models.Model):
    id = fields.IntField(pk=True)
    t_numero_letra = fields.CharField(max_length=20, unique=True, index=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # M2M hacia CasaApartamento a través del modelo intermedio (con campos extra)
    #casas_apartamentos = fields.ManyToManyField(
    #    "models.CasaApartamento",
    #    through="models.CasaApartamentoInteriorTorre",
    #    through_fields=("torre_interior", "casa_apartamento"),
    #    related_name="interiores",
    #)

    class Meta:
        table = "ph_torres_interiores"
        indexes = [("t_numero_letra",), ("is_active",)]

    def __str__(self) -> str:
        return f"<TorreInterior {self.id} {self.t_numero_letra} {'active' if self.is_active else 'inactive'}>"
