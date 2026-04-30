from tortoise import fields, models

class CasaApartamento(models.Model):
    id = fields.IntField(pk=True)
    c_numero_letra = fields.CharField(max_length=20, unique=True, index=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # M2M hacia TorreInterior a través del modelo intermedio (con campos extra)
    #no se puede tener en ambos modelos el related_name igual
    #interiores = fields.ManyToManyField(
    #    "models.TorreInterior",
    #    through="models.CasaApartamentoInteriorTorre",
    #    through_fields=("casa_apartamento", "torre_interior"),
    #    related_name="casas_apartamentos",
    #)

    class Meta:
        table = "ph_casas_apartamentos"
        indexes = [("c_numero_letra",), ("is_active",)]

    def __str__(self) -> str:
        return f"<CasaApartamento {self.id} {self.c_numero_letra} {'active' if self.is_active else 'inactive'}>"
