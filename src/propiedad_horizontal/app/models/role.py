from tortoise import fields, models


class Role(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, index=True)
    description = fields.CharField(max_length=255, null=True)

    #permissions = fields.ManyToManyField("models.Permission", related_name="roles") se movió a Permission para evitar circularidad
    users = fields.ReverseRelation["User"]

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "roles"

    def __str__(self) -> str:
        return f"<Rol {self.id} {self.name}>"
    
    @classmethod
    async def seed_defaults(cls):
        """
        Inicializa un rol por defecto.
        Solo crea registros si no existen.
        """
        defaults = [
            {"name": "superadmin", "description": "Administrador principal del aplicativo, con todos los permisos."},
        ]
        for d in defaults:
            exists = await cls.filter(name=d["name"]).exists()
            if not exists:
                await cls.create(**d)
