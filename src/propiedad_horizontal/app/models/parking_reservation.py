from tortoise import fields, models
from tortoise.validators import MinLengthValidator
from propiedad_horizontal.app.domain.enums import ReservationStatus

class VisitorReservation(models.Model):
    """
    Modelo para reservas de parqueadero de visitantes.
    
    Campos principales:
    - spot: referencia al puesto de parqueadero (ParkingSpot)
    - casa_interior_torre_link: relación a CasaApartamentoInteriorTorre (que integra torre + apartamento)
    - visitor_*: datos del visitante (documento, nombre, email, celular)
    - starts_at / ends_at: período de la reserva
    - billed_minutes: minutos a facturar
    - total_price: precio total calculado
    - status: estado actual de la reserva (ACTIVE, CANCELLED, etc.)
    """
    id = fields.IntField(pk=True)
    spot = fields.ForeignKeyField("models.ParkingSpot", related_name="visitor_reservations", on_delete=fields.CASCADE)
    casa_interior_torre_link = fields.ForeignKeyField(
        "models.CasaApartamentoInteriorTorre",
        related_name="visitor_reservations",
        on_delete=fields.CASCADE
    )

    visitor_type_document = fields.CharField(max_length=3, null=False)  # CC, TI, NIT, etc.
    visitor_document_number = fields.CharField(max_length=12, null=False)
    visitor_name = fields.CharField(max_length=100, null=False)
    visitor_email = fields.CharField(max_length=100, null=False)
    visitor_cell = fields.CharField(
        max_length=25,
        null=False,
        validators=[MinLengthValidator(min_length=10)]
    )

    # Vehículo - relación al modelo administrativo
    vehicle_type_id = fields.IntField()
    vehicle_code = fields.CharField(max_length=20, null=False)  # Placa u otro identificador

    # Identificador del QR enviado al visitante (uuid hex). Se utiliza para validar escaneos.
    qr_token = fields.CharField(max_length=64, unique=True, null=False)
    qr_generated_at = fields.DatetimeField(null=True)

    # Período de la reserva
    starts_at = fields.DatetimeField()
    ends_at = fields.DatetimeField()

    # Facturación
    billed_minutes = fields.IntField()  # Minutos a facturar
    total_price = fields.DecimalField(max_digits=12, decimal_places=2)  # Precio total

    status = fields.CharEnumField(ReservationStatus, default=ReservationStatus.ACTIVE)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "parking_visitor_reservations"
        # Índice para búsquedas rápidas de disponibilidad en un puesto
        indexes = [("spot_id", "starts_at", "ends_at")]
