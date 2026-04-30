from tortoise import fields, models

class Persona(models.Model):
    id = fields.IntField(pk=True)

    # CORRECCIÓN: La persona ahora se asocia a la relación Torre->Casa/Apartamento (CasaApartamentoInteriorTorre)
    # Esto permite identificar correctamente la ubicación de la persona: qué casa/apartamento Y en qué torre/interior
    casa_interior_link = fields.ForeignKeyField(
        "models.CasaApartamentoInteriorTorre",
        related_name="personas",
        on_delete=fields.CASCADE,
    )

    # Asociación opcional a Usuario (autenticación)
    usuario = fields.ForeignKeyField(
        "models.User",
        related_name="personas",
        null=True,
        on_delete=fields.SET_NULL,
    )

    # Datos personales
    nombres = fields.CharField(max_length=120, index=True)
    apellidos = fields.CharField(max_length=120, index=True)
    edad = fields.IntField()
    celular = fields.CharField(max_length=20, null=True)
    email = fields.CharField(max_length=150, null=True, index=True)

    # Flags
    is_propietario = fields.BooleanField(default=False)
    is_arrendatario = fields.BooleanField(default=False)
    acepta_terminosycondiciones = fields.BooleanField(default=False)

    # Soft delete
    is_active = fields.BooleanField(default=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "personas"
        indexes = [
            # CORRECCIÓN: El índice ahora usa casa_interior_link_id en lugar de casa_apartamento_id
            ("casa_interior_link_id", "is_active"),
            ("is_propietario", "is_arrendatario"),
            ("nombres", "apellidos"),
        ]

    def __str__(self) -> str:
        # CORRECCIÓN: Muestra el ID del link en lugar del ID de casa/apartamento
        return f"<Persona {self.id} {self.nombres} {self.apellidos} Link:{self.casa_interior_link_id} {'active' if self.is_active else 'inactive'}>"
