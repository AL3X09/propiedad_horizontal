from tortoise import fields, models

class PropiedadHorizontal(models.Model):
    id = fields.IntField(pk=True)

    nombre = fields.CharField(max_length=150, index=True)
    direccion = fields.CharField(max_length=200)
    telefono = fields.CharField(max_length=20, null=True)  # deja str para ceros/lada
    localidad = fields.CharField(max_length=100, null=True)
    barrio = fields.CharField(max_length=100, null=True)
    correo = fields.CharField(max_length=150, null=True, index=True)  # puedes validar en schema/servicio

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "horizontal_properties"
        indexes = [("nombre",), ("correo",)]

    def __str__(self) -> str:
        return f"<PH {self.id} {self.nombre}>"
