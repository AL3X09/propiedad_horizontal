from tortoise import fields, models

class VehicleType(models.Model):
    """
    Modelo administrativo para gestionar los tipos de vehículo.
    Se inicializa con los valores del enum VehicleType (del domain).
    """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    emoji = fields.CharField(max_length=10, null=True)
    description = fields.CharField(max_length=255, null=True)
    display_order = fields.IntField(default=0)
    is_active = fields.BooleanField(default=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "vehicle_types"
        indexes = [("is_active", "display_order")]

    def __str__(self) -> str:
        return f"<Vehiculo {self.code} {self.name} {'active' if self.is_active else 'inactive'}>"

    @classmethod
    async def seed_defaults(cls):
        """
        Inicializa los tipos de vehículo por defecto basándose en el enum VehicleType.
        Solo crea registros si no existen.
        """
        defaults = [
            {"name": "Carro", "emoji": "🚗", "display_order": 1},
            {"name": "Moto", "emoji": "🏍️", "display_order": 2},
            {"name": "Cicla", "emoji": "🚴", "display_order": 3},
            {"name": "Cicla eléctrica", "emoji": "🚴‍♀️", "display_order": 4},
            {"name": "Patineta eléctrica", "emoji": "🛴", "display_order": 5},
        ]
        for d in defaults:
            exists = await cls.filter(name=d["name"]).exists()
            if not exists:
                await cls.create(**d)