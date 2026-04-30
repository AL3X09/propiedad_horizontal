from tortoise import fields, models
from propiedad_horizontal.app.domain.enums import AssignmentStatus

class MonthlyAssignment(models.Model):
    id = fields.IntField(pk=True)
    spot = fields.ForeignKeyField("models.ParkingSpot", related_name="assignments", on_delete=fields.CASCADE)
    # Relación con Persona: el asignatario del parqueadero es una persona, no un usuario de autenticación
    persona = fields.ForeignKeyField("models.Persona", related_name="parking_assignments", on_delete=fields.CASCADE)

    # Vehículo asignado - relación al modelo administrativo
    vehicle_type_id = fields.IntField()
    #vehicle_code = fields.CharField(max_length=20, null=False)  # Placa u otro identificador

    start_date = fields.DateField()
    months = fields.IntField()  # 1..6
    end_date = fields.DateField()

    status = fields.CharEnumField(AssignmentStatus, default=AssignmentStatus.ACTIVE)

    monthly_price = fields.CharField(max_length=10)
    total_price = fields.CharField(max_length=12)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "parking_monthly_assignments"
        indexes = [("spot_id", "start_date", "end_date")]
