from datetime import date
from decimal import Decimal
from typing import List, Optional

from propiedad_horizontal.app.models.parking import ParkingSpot
from propiedad_horizontal.app.models.persona import Persona
from propiedad_horizontal.app.models.parking_assignment import MonthlyAssignment
from propiedad_horizontal.app.models.vehicle_type import VehicleType
from propiedad_horizontal.app.schemas.parking_assignment import MonthlyAssignmentCreate
from propiedad_horizontal.app.domain.enums import AssignmentStatus

def _add_months(start: date, months: int) -> date:
    # Suma de meses sin dependencias externas (simple: avanza año/mes, conserva día si posible)
    y = start.year + (start.month - 1 + months) // 12
    m = (start.month - 1 + months) % 12 + 1
    d = start.day
    # Ajuste de fin de mes (para días que no existen, ej. 31 febrero): retrocede al último día del mes
    # Asumimos 28/29/30/31 lógica simple
    import calendar
    last_day = calendar.monthrange(y, m)[1]
    if d > last_day:
        d = last_day
    return date(y, m, d)

async def _has_overlap_for_spot(spot_id: int, start: date, end: date) -> bool:
    """
    Verifica solape con asignaciones mensuales (ACTIVE) y reservas de visitantes (ACTIVE):
    - overlap si start < existing.end AND end > existing.start
    """
    # Asignaciones
    assign_overlap = await MonthlyAssignment.filter(
        spot_id=spot_id,
        status=AssignmentStatus.ACTIVE,
        start_date__lt=end,
        end_date__gt=start,
    ).exists()

    if assign_overlap:
        return True

    # Reservas (convierten Date a Datetime: una reserva de horas dentro del rango bloquea)
    from propiedad_horizontal.app.models.parking_reservation import VisitorReservation, ReservationStatus
    # tomamos el rango start 00:00 a end 23:59:59 para comparar
    import datetime as dt
    start_dt = dt.datetime.combine(start, dt.time.min)
    end_dt = dt.datetime.combine(end, dt.time.max)

    reserv_overlap = await VisitorReservation.filter(
        spot_id=spot_id,
        status=ReservationStatus.ACTIVE,
        starts_at__lt=end_dt,
        ends_at__gt=start_dt,
    ).exists()

    return reserv_overlap

async def create_monthly_assignment(data: MonthlyAssignmentCreate) -> MonthlyAssignment:
    if not (1 <= data.months <= 6):
        raise ValueError("La permanencia debe ser entre 1 y 6 meses.")

    spot = await ParkingSpot.get_or_none(id=data.spot_id)
    if not spot or not spot.is_active:
        raise ValueError("Parqueadero no existente o inactivo.")

    persona = await Persona.get_or_none(id=data.persona_id)
    if not persona or not persona.is_active:
        raise ValueError("Persona no encontrada o inactiva.")

    # Validar que el tipo de vehículo existe y está activo
    vehicle_type = await VehicleType.get_or_none(id=data.vehicle_type_id, is_active=True)
    if not vehicle_type:
        raise ValueError("Tipo de vehículo no encontrado o inactivo.")

    end_date = _add_months(data.start_date, data.months)

    # Chequeo de disponibilidad
    overlap = await _has_overlap_for_spot(spot.id, data.start_date, end_date)
    if overlap:
        raise ValueError("El parqueadero no está disponible en el rango solicitado.")

    # Convertir precios a string para almacenar en CharField
    monthly_price_decimal = Decimal(spot.monthly_price)
    total_price_decimal = monthly_price_decimal * data.months
    monthly_price_str = str(monthly_price_decimal)
    total_price_str = str(total_price_decimal)

    assignment = await MonthlyAssignment.create(
        spot_id=spot.id,
        persona_id=persona.id,
        start_date=data.start_date,
        months=data.months,
        end_date=end_date,
        vehicle_type_id=data.vehicle_type_id,
        status=AssignmentStatus.ACTIVE,
        monthly_price=monthly_price_str,
        total_price=total_price_str,
    )
    return assignment

async def list_assignments(limit: int = 100, offset: int = 0) -> List[MonthlyAssignment]:
    # Se elimina select_related para evitar joins innecesarios; los IDs están disponibles directamente en el modelo
    return await MonthlyAssignment.all().offset(offset).limit(limit).order_by("-start_date")

async def get_assignment(assignment_id: int) -> Optional[MonthlyAssignment]:
    # Corrección: obtener el queryset con select_related y luego first(), ya que get_or_none no permite encadenar select_related
    return await MonthlyAssignment.filter(id=assignment_id).select_related("spot", "persona").first()

async def cancel_assignment(assignment_id: int) -> bool:
    a = await MonthlyAssignment.get_or_none(id=assignment_id)
    if not a:
        return False
    a.status = AssignmentStatus.CANCELLED
    await a.save()
    return True
