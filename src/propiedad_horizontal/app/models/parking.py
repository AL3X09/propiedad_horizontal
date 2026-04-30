from tortoise import fields, models
from propiedad_horizontal.app.domain.enums.parking_spot_status import ParkingSpotStatus


class ParkingSpot(models.Model):
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=20, unique=True, index=True)  # el codigo del parqueadero ej. "A-01"
    vehicle_type_id = fields.IntField()  # FK al modelo VehicleType
    is_parking_public = fields.BooleanField(default=False) # Si si es sinónimo es para uso de publico externo o público general.
    is_active = fields.BooleanField(default=True)

    monthly_price = fields.CharField(max_length=20)  # por mes (usuarios) - se guarda como string
    minute_price = fields.CharField(max_length=20)   # por hora (visitantes) - se guarda como string

    parking_status = fields.CharEnumField(ParkingSpotStatus, default=ParkingSpotStatus.AVIABLE)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    

    class Meta:
        table = "parking_spots"

    def __str__(self) -> str:
        return f"<ParkingSpot {self.code} {self.vehicle_type_id} {self.is_parking_public} {self.parking_status} {'active' if self.is_active else 'inactive'}>"
