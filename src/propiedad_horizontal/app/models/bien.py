from tortoise import fields, models


class Bien(models.Model):
    id = fields.IntField(pk=True)

    tipo = fields.CharField(max_length=100, index=True)
    descripcion = fields.CharField(max_length=255, null=True)

    is_active = fields.BooleanField(default=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "bienes"
        indexes = [
            ("tipo", "descripcion"),
            ("is_active",),
        ]

    def __str__(self) -> str:
        return f"<Bien {self.id} {self.tipo} descripcion={self.descripcion} active={self.is_active}>"
    
    @classmethod
    async def seed_defaults(cls):
        """
        Inicializa los bienes.
        Solo crea registros si no existen.
        """
        defaults = [
            {"tipo": "Nevera", "descripcion": ""},
            {"tipo": "Televisor", "descripcion": ""},
            {"tipo": "Cama", "descripcion": ""},
            {"tipo": "Comedor", "descripcion": ""},
            {"tipo": "Lavadora eléctrica", "descripcion": ""},
            {"tipo": "Estufa", "descripcion": ""},
            {"tipo": "Aspiradora", "descripcion": ""},
        ]
        for d in defaults:
            exists = await cls.filter(tipo=d["tipo"]).exists()
            if not exists:
                await cls.create(**d)
