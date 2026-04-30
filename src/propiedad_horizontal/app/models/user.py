from tortoise import fields, models


class User(models.Model):
    id = fields.IntField(pk=True)

    username = fields.CharField(max_length=50, unique=True, index=True)
    password_hash = fields.CharField(max_length=128)
    is_active = fields.BooleanField(default=True)
    role = fields.ForeignKeyField("models.Role", related_name="users", on_delete=fields.CASCADE)
    
    # Nuevo campo para forzar cambio de contraseña
    must_change_password = fields.BooleanField(default=True)
    # Opcional: registrar cuándo fue el último cambio
    password_changed_at = fields.DatetimeField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

    def __str__(self) -> str:
        role_name = getattr(self.role, "name", None)
        return f"<Usuario {self.id} {self.username} {role_name}>"
    
    @classmethod
    async def seed_defaults(cls):
        from propiedad_horizontal.app.models.role import Role  # import local evita circularidad

        role = await Role.get(name="superadmin")  # obtiene la instancia real

        defaults = [
            {
                "username": "superadmin",
                "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$zVkr5XxPCYHQmrPW+h/DmA$oTSUlz1Cj0idwfeu9C0it8ihGI8/attEhg7RmE35Stw",
                "role": role,           # ✅ instancia, no string
                "must_change_password": False,
            },
        ]
        for d in defaults:
            exists = await cls.filter(username=d["username"]).exists()
            if not exists:
                await cls.create(**d)