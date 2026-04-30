from typing import List, Optional
from decimal import Decimal
from math import ceil
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi import BackgroundTasks, Query, HTTPException


from propiedad_horizontal.app.core.config import settings, APP_TIMEZONE
from propiedad_horizontal.app.utils.qr import generate_qr_base64
from propiedad_horizontal.app.utils.email_renderer import (
    render_checkout_email,
    render_reservation_confirmation,
)
from propiedad_horizontal.app.services.notification_client import notification_client
from propiedad_horizontal.app.models.parking import ParkingSpot
from propiedad_horizontal.app.models.parking_reservation import VisitorReservation
from propiedad_horizontal.app.models.casa_apartamento_interior_torre import CasaApartamentoInteriorTorre
from propiedad_horizontal.app.models.torre_interior import TorreInterior
from propiedad_horizontal.app.models.casa_apartamento import CasaApartamento
from propiedad_horizontal.app.models.vehicle_type import VehicleType
from propiedad_horizontal.app.models.persona import Persona
from propiedad_horizontal.app.domain.enums import ReservationStatus, ParkingSpotStatus, AssignmentStatus

BOGOTA_TZ = ZoneInfo(APP_TIMEZONE)

async def _spot_disponible(vehicle_type_id: int):
    # evitar que se solape con otras reservas
    spot_disponible = await ParkingSpot.filter(
        parking_status=ParkingSpotStatus.AVIABLE,
        vehicle_type_id=vehicle_type_id,
        is_active=True,
    ).first()
    if spot_disponible:
        return spot_disponible
    else:
        return None
    
async def _id_interior_apto(torre:str,casa_apto:str) -> int:
    torre = await TorreInterior.get_or_none(t_numero_letra=torre)
    casa_apto = await CasaApartamento.get_or_none(c_numero_letra=casa_apto)
    
    casa_apto_id = await CasaApartamentoInteriorTorre.filter(
        casa_apartamento=torre.id, #busco el parqueadero disponible
        torre_interior=casa_apto.id
    ).first()  # Obtiene el primer objeto o None
    if casa_apto_id:
        return casa_apto_id.id  # Retorna list spot encontrado
    else:
        return None  # O lanzar una excepción si no hay spots disponibles

async def _id_spot_disponible(vehicle_type_id: int) -> int | None:
    # Solape con otras reservas
    spot_disponible = await ParkingSpot.filter(
        parking_status=ParkingSpotStatus.AVIABLE,
        vehicle_type_id=vehicle_type_id,
        is_active=True,
    ).first()
    if spot_disponible:
        return spot_disponible.id
    else:
        return None


async def _has_overlap_for_spot_datetime(spot_id: int, start_dt: datetime, end_dt: datetime) -> bool:
    # Solape con otras reservas
    reserv_overlap = await VisitorReservation.filter(
        spot_id=spot_id,
        status=ReservationStatus.ACTIVE,
        starts_at__lt=end_dt,
        ends_at__gt=start_dt,
    ).exists()
    if reserv_overlap:
        return True

    # Solape con asignaciones mensuales (si coincide el rango horario dentro del periodo de asignación)
    from propiedad_horizontal.app.models.parking_assignment import MonthlyAssignment, AssignmentStatus
    assign_overlap = await MonthlyAssignment.filter(
        spot_id=spot_id,
        status=AssignmentStatus.ACTIVE,
        start_date__lt=end_dt.date(),
        end_date__gt=start_dt.date(),
    ).exists()
    return assign_overlap


async def _find_available_spot(vehicle_type_id: int, starts_at: datetime, ends_at: datetime) -> ParkingSpot | None:
    """Busca un spot disponible que no tenga solapamiento con reservas o asignaciones."""
    candidates = await ParkingSpot.filter(
        parking_status=ParkingSpotStatus.AVIABLE,
        vehicle_type_id=vehicle_type_id,
        is_active=True,
    ).order_by("id").all()

    for spot in candidates:
        if not await _has_overlap_for_spot_datetime(spot.id, starts_at, ends_at):
            return spot
    return None

async def _compute_total_price(reservation: VisitorReservation) -> Decimal:
    """Cálculo simple: billed_minutes × minute_price. Usado para referencia solo."""
    spot = await reservation.spot
    return Decimal(reservation.billed_minutes) * spot.minute_price


async def _compute_total_price_checkout(reservation: VisitorReservation) -> tuple[Decimal, str]:
    """
    Calcula el precio final al finalizar la reserva (checkout/salida).
    
    **Lógica de cálculo:**
    1. Tiempo real = ends_at - starts_at (en minutos)
    2. Si tiempo_real < billed_minutes:
       - Si la diferencia es ≤ 4 min: cobrar billed_minutes (tolerancia)
       - Si la diferencia es > 4 min: cobrar tiempo_real
    3. Si tiempo_real > billed_minutes:
       - Si supera por ≤ 5 min: cobrar billed_minutes (tolerancia)
       - Si supera por > 5 min: cobrar billed_minutes + $5.000 de recargo
    
    Args:
        reservation: Objeto VisitorReservation con starts_at, ends_at, billed_minutes
    
    Returns:
        tuple (total_price: Decimal, detalle: str): Precio total y desglose para el correo
    """
    spot = await reservation.spot
    minute_price = Decimal(spot.minute_price)
    
    # Calcular tiempo real transcurrido
    # Normalizar a timezone Bogotá si son naive para que la resta funcione correctamente
    starts = reservation.starts_at
    ends = reservation.ends_at
    
    if starts.tzinfo is not None:
        starts = starts.astimezone(BOGOTA_TZ)
    else:
        starts = starts.replace(tzinfo=BOGOTA_TZ)
    
    if ends.tzinfo is not None:
        ends = ends.astimezone(BOGOTA_TZ)
    else:
        ends = ends.replace(tzinfo=BOGOTA_TZ)
    
    tiempo_real_segundos = (ends - starts).total_seconds()
    tiempo_real_minutos = tiempo_real_segundos / 60.0
    
    billed_minutes = reservation.billed_minutes
    diferencia = tiempo_real_minutos - billed_minutes
    
    minutos_a_cobrar = billed_minutes
    recargo_adicional = Decimal(0)
    desglose = ""
    
    if diferencia < 0:
        # Duraron menos que billed_minutes
        if abs(diferencia) <= 4:
            # Tolerancia: cobrar billed_minutes completos
            minutos_a_cobrar = billed_minutes
            desglose = f"Tiempo real: {tiempo_real_minutos:.1f} min. Se cobra billed_minutes ({billed_minutes} min) por tolerancia."
        else:
            # Sin tolerancia: cobrar lo que realmente usó
            minutos_a_cobrar = int(tiempo_real_minutos)
            desglose = f"Tiempo real: {tiempo_real_minutos:.1f} min < {billed_minutes} min facturados. Se cobra solo tiempo usado."
    elif diferencia > 0:
        # Duraron más que billed_minutes
        if diferencia <= 5:
            # Tolerancia: cobrar billed_minutes sin recargo
            minutos_a_cobrar = billed_minutes
            desglose = f"Tiempo excedido: {diferencia:.1f} min ≤ 5 min. Se cobra billed_minutes sin recargo."
        else:
            # Supera tolerancia: recargo de $5.000
            minutos_a_cobrar = billed_minutes
            recargo_adicional = Decimal(5000)
            desglose = f"Tiempo excedido: {diferencia:.1f} min > 5 min. Se cobra billed_minutes + $5.000 de recargo."
    else:
        # Exactamente el tiempo
        desglose = f"Tiempo exacto: {tiempo_real_minutos:.1f} min = {billed_minutes} min."
    
    total_price = (Decimal(minutos_a_cobrar) * minute_price) + recargo_adicional
    
    # Desglose completo
    resumen = (
        f"{desglose}\n"
        f"Minutos cobrados: {minutos_a_cobrar}\n"
        f"Tarifa por minuto: ${minute_price:,.0f} COP\n"
        f"Subtotal: ${Decimal(minutos_a_cobrar) * minute_price:,.0f} COP\n"
    )
    if recargo_adicional > 0:
        resumen += f"Recargo por exceso: ${recargo_adicional:,.0f} COP\n"
    resumen += f"**TOTAL A PAGAR: ${total_price:,.0f} COP**"
    
    return total_price, resumen


async def send_checkout_email(reservation: VisitorReservation, total_price: Decimal, desglose: str):
    """
    Envía email de recibo al finalizar la reserva con el costo total.
    
    Se ejecuta como background task cuando el visitante escanea por segunda vez
    (checkout / salida del parqueadero).
    
    Args:
        reservation: Objeto VisitorReservation finalizado
        total_price: Precio total a cobrar (Decimal)
        desglose: Detalle del cálculo de precio
    """
    try:
        # Formatear información
        spot = await reservation.spot
        spot_number = str(spot.code) if spot else "TBD"
        
        # Función helper para formatear fecha - maneja tanto naive como aware datetimes
        def format_datetime(dt):
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=BOGOTA_TZ)
            return dt.astimezone(BOGOTA_TZ).strftime("%d/%m/%Y a las %H:%M")
        
        starts_at_formatted = format_datetime(reservation.starts_at)
        ends_at_formatted = format_datetime(reservation.ends_at)
        total_price_formatted = f"${total_price:,.0f} COP"
        
        # Renderizar HTML desde template
        html_body = render_checkout_email(
            visitor_name=reservation.visitor_name,
            reservation_id=reservation.id,
            spot_number=spot_number,
            starts_at_formatted=starts_at_formatted,
            ends_at_formatted=ends_at_formatted,
            price_breakdown=desglose,
            total_price_formatted=total_price_formatted,
        )
        
        # Enviar email via servicio de notificaciones (API REST)
        await notification_client.enviar_email(
            to_email=reservation.visitor_email,
            subject=f"✅ Recibo: Parqueadero #{reservation.id} - ${total_price:,.0f} COP",
            html_content=html_body,
        )
        
    except Exception as e:
        import sys
        print(f"Error al enviar email de checkout para reserva {reservation.id}: {str(e)}", file=sys.stderr)


async def _populate_qr(reservation: VisitorReservation):
    reservation.qr_token = uuid4().hex
    reservation.qr_generated_at = datetime.now(BOGOTA_TZ)
    await reservation.save()



async def create_reservation(spot_id: int, casa_apto_interior_torre_id: int, starts_at: datetime, ends_at: datetime, visitor_type_document: str, visitor_document_number: str, visitor_name: str, visitor_email: str, visitor_cell: str, vehicle_type_id: int, vehicle_code: str, billed_minutes: int, background_tasks: BackgroundTasks) -> VisitorReservation:
    
    #print("Creating reservation...", f"Starts At: {starts_at}, Ends At: {ends_at}, Billed Minutes: {billed_minutes}, starts_at type: {type(starts_at)}, ends_at type: {type(ends_at)}")
    # Las fechas que llegan del frontend ya están en hora de Colombia (Bogotá)
    # No se hace ninguna conversión de timezone - se almacenan tal cual
    # El frontend envía la fecha en formato naive (sin timezone) representando hora de Bogotá
    if ends_at <= starts_at:
        raise ValueError("La hora de finalización debe ser posterior al inicio.")
    if len(visitor_type_document)  < 2 or len(visitor_type_document) > 3:
        raise ValueError("El tipo de documento debe tener una logitud igual a 3 caracteres.")
    if len(visitor_document_number) < 5 or len(visitor_document_number) > 20 or not visitor_document_number.isdigit():
        raise ValueError("La longitud del número de documento debe estar entre 5 a 20 caracteres y debe ser un valor numérico.")
    if len(visitor_cell) != 10 or not visitor_cell.isdigit():
        raise ValueError("La longitud del número de celular debe ser de 10 caracteres y debe ser un valor numérico.")
    # Validar que el tipo de vehículo existe y está activo
    vehicle_type = await VehicleType.get_or_none(id=vehicle_type_id, is_active=True)
    if not vehicle_type:
        raise ValueError("Tipo de vehículo no encontrado o inactivo.")
    if not vehicle_code or len(vehicle_code) < 2 or len(vehicle_code) > 20:
        raise ValueError("El código del vehículo (placa) debe tener entre 2 y 20 caracteres.")
    # validar el valor de billed_minutes enviado por la API
    if billed_minutes is None or not isinstance(billed_minutes, int):
        raise ValueError("Los minutos facturados deben enviarse como un entero.")
    if billed_minutes < 0:
        raise ValueError("Los minutos facturados no pueden ser negativos.")
    
    spot = None
    if isinstance(spot_id, int) and spot_id > 0:
        requested_spot = await ParkingSpot.get_or_none(
            id=spot_id,
            parking_status=ParkingSpotStatus.AVIABLE,
            vehicle_type_id=vehicle_type_id,
            is_active=True,
        )
        if requested_spot and not await _has_overlap_for_spot_datetime(requested_spot.id, starts_at, ends_at):
            spot = requested_spot

    if not spot:
        spot = await _find_available_spot(vehicle_type_id, starts_at, ends_at)

    if not spot:
        raise ValueError("No hay parqueaderos disponibles en el rango solicitado.")

    spot_id = spot.id
    
    # Validar máximo 3 reservas activas por email
    existing = await VisitorReservation.filter(
        visitor_email=visitor_email,
        status__in=[ReservationStatus.ACTIVE, ReservationStatus.COMPLETED]
    ).count()
    if existing >= 3:
        raise ValueError("Máximo 3 reservas activas por email.")
        
    #print("Spot:", spot)
    #print("Spot ID:", spot_id)

    #if overlap:
    #    raise ValueError("El parqueadero no está disponible en el rango solicitado.")

    # Determinar minutos facturados. El caller puede enviar un valor explícito
    # (por ejemplo, desde la UI), en cuyo caso lo respetamos siempre y cuando
    # sea positivo. Si se pasa cero o negativo, se calcula a partir del rango
    # horario; en ese caso y sólo en ese caso se aplica la regla "mínimo 1 hora".
    if billed_minutes and billed_minutes > 0:
        # aceptar el valor enviado, pero asegurarse de que la duración no sea
        # absurda (opcionales: podríamos comparar contra la diferencia de hora).
        pass
    else:
        total_minutes = (ends_at - starts_at).total_seconds() / 60.0
        billed_minutes = max(1, int(ceil(total_minutes)))
        if billed_minutes < 1:
            billed_minutes = 60  # Mínimo una hora

    #hourly_price: Decimal = Decimal(spot.hourly_price)
    #total_price = hourly_price * billed_minutes

    reservation = await VisitorReservation.create(
        spot_id=spot_id,
        starts_at=starts_at,
        ends_at=ends_at,
        casa_interior_torre_link_id=casa_apto_interior_torre_id,
        visitor_type_document=visitor_type_document,
        visitor_document_number=visitor_document_number,
        visitor_name=visitor_name,
        visitor_email=visitor_email,
        visitor_cell=visitor_cell,
        vehicle_type_id=vehicle_type_id,
        vehicle_code=vehicle_code.upper(),
        billed_minutes=billed_minutes,
        total_price='0',
        status=ReservationStatus.ACTIVE,
        qr_token="",
        qr_generated_at=None
    )
    await _populate_qr(reservation)
    # enviar correo en segundo plano
    background_tasks.add_task(send_reservation_qr, reservation)
    return reservation


# -- helpers adicionales --------------------------------------------------
async def send_reservation_qr(reservation: VisitorReservation):
    """
    Envía el email de confirmación de reserva con QR embebido en el cuerpo.
    
    Se ejecuta como background task para no bloquear la respuesta HTTP.
    
    Funcionalidades:
    - Genera QR como imagen base64 embebida en HTML (no adjunto)
    - Email HTML atractivo y responsive
    - Saludo personalizado al visitante
    - Información completa de la reserva
    - Compatible con todos los clientes de email
    
    Args:
        reservation: Objeto VisitorReservation con los datos de la reserva
    
    Nota:
        Esta función se ejecuta en background, así que los errores se logean
        pero no se retornan al cliente.
    """
    try:
        # Obtener URL base de la API
        base_url = settings.API_URL or "http://localhost:8000"
        
        # Generar QR como base64 (embebido en HTML, no adjunto)
        qr_base64 = generate_qr_base64(
            reservation_id=reservation.id,
            token=reservation.qr_token,
            base=base_url
        )
        
        # Obtener información del puesto de parqueadero
        spot = await reservation.spot
        spot_number = str(spot.code) if spot else "TBD"
        
        # Función helper para formatear fecha - maneja tanto naive como aware datetimes
        def format_datetime(dt):
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=BOGOTA_TZ)
            return dt.astimezone(BOGOTA_TZ).strftime("%d/%m/%Y a las %H:%M")
        
        # Formatear fechas de manera legible
        starts_at_formatted = format_datetime(reservation.starts_at)
        ends_at_formatted = format_datetime(reservation.ends_at)
        # Formatear precio (asumir COP si no hay otra moneda)
        total_price_formatted = f"${reservation.total_price:,.0f} COP"
        
        # Obtener el tipo de vehículo con label (incluye emoji)
        vehicle_type = await VehicleType.get_or_none(id=reservation.vehicle_type_id)
        if vehicle_type:
            vehicle_type_label = f"{vehicle_type.emoji or ''} {vehicle_type.name}".strip()
        else:
            vehicle_type_label = f"Tipo de vehículo #{reservation.vehicle_type_id}"
        
        # Renderizar HTML del email desde template
        html_body = render_reservation_confirmation(
            visitor_name=reservation.visitor_name,
            reservation_id=reservation.id,
            qr_base64=qr_base64,
            spot_number=spot_number,
            vehicle_code=reservation.vehicle_code,
            vehicle_type=vehicle_type_label,
            starts_at=starts_at_formatted,
            ends_at=ends_at_formatted,
            total_price=total_price_formatted,
        )
        
        # Enviar email via servicio de notificaciones (API REST)
        await notification_client.enviar_email(
            to_email=reservation.visitor_email,
            subject=f"✅ Confirmación: Reserva de Parqueadero #{reservation.id}",
            html_content=html_body,
        )
        
        # Enviar email via servicio de notificaciones (API REST)
        await notification_client.enviar_sms(
            message_body=f"Fontibon reservardo te da la bienvenida, {reservation.visitor_name}, todo el proceso llegara al correo que registraste.",
            to_number=f"+57{reservation.visitor_cell}",
        )
        
    except Exception as e:
        # Loguear error sin bloquear la ejecución
        import sys
        print(f"Error al enviar email de reserva {reservation.id}: {str(e)}", file=sys.stderr)
        # En producción, considera usar un logger apropiado aquí


async def scan_qr(reservation_id: int, token: str, background_tasks: BackgroundTasks = None) -> VisitorReservation:
    """
    Valida y procesa el escaneo del QR para una reserva.
    
    Transiciones permitidas:
    - ACTIVE → COMPLETED (primer escaneo: visitante llega)
    - COMPLETED → FINISHED (segundo escaneo: visitante se va)
    - Otros estados: rechaza con error descriptivo
    
    Nuevas reglas adicionales para el primer escaneo:
    * Si el visitante escanea pasados **10 minutos** desde `starts_at`
      la reserva pasa a `VIOLATED` (incumplida) y se retorna error 410.
      El campo `updated_at` se actualiza con la hora actual.

    When transitioning to FINISHED:
    - Calculates final price with tolerance rules and surcharges
    - Updates total_price in database
    - Sends checkout email with receipt in background
    
    Args:
        reservation_id: ID de la reserva
        token: Token QR validación hexadecimal
        background_tasks: Tareas asincrónicas para enviar correo
    
    Returns:
        VisitorReservation: Reserva actualizada tras escaneo
    
    Raises:
        HTTPException: Si reserva no existe, token inválido, estado no permite escaneo,
                      o la reserva fue violada por llegada tardía
    """
    if background_tasks is None:
        background_tasks = BackgroundTasks()
    # Buscar reserva
    r = await VisitorReservation.get_or_none(id=reservation_id)
    if not r:
        raise HTTPException(
            status_code=404,
            detail=f"Reserva #{reservation_id} no encontrada"
        )
    
    # Validar token QR (separado de la búsqueda para seguridad)
    if r.qr_token != token:
        raise HTTPException(
            status_code=401,
            detail="Token QR inválido para esta reserva"
        )
    
    # Validar que no esté cancelada (no se puede usar)
    if r.status == ReservationStatus.CANCELLED:
        raise HTTPException(
            status_code=410,
            detail="La reserva fue cancelada y no puede ser utilizada"
        )
    
    # Validar que no esté finalizada (no se puede rescanning)
    if r.status == ReservationStatus.FINISHED:
        raise HTTPException(
            status_code=409,
            detail="La reserva ya fue finalizada. El visitante ya liberó el parqueadero"
        )
    
    # Procesar escaneo según estado actual
    now = datetime.now(BOGOTA_TZ)
    print(f"fecha es {now} ")
    
    # Normalizar starts_at para comparación: si tiene timezone, convertir a Bogotá; si no, usar directo
    if r.starts_at.tzinfo is not None:
        starts_at_bogota = r.starts_at.astimezone(BOGOTA_TZ)
    else:
        starts_at_bogota = r.starts_at.replace(tzinfo=BOGOTA_TZ)
    
    if r.status == ReservationStatus.ACTIVE:
        # Primer escaneo: visitante llega al parqueadero
        # si se presenta más de 10 minutos después de la hora de inicio,
        # consideramos que perdió la reserva (incumplida).
        late_threshold = starts_at_bogota + timedelta(minutes=10)
        if now > late_threshold:
            r.status = ReservationStatus.VIOLATED
            r.updated_at = now
            await r.save()
            raise HTTPException(
                status_code=410,
                detail="Reserva incumplida: el visitante llegó más de 10 minutos tarde"
            )
        r.status = ReservationStatus.COMPLETED
    elif r.status == ReservationStatus.COMPLETED:
        # Segundo escaneo: visitante se va del parqueadero
        r.status = ReservationStatus.FINISHED
        # Almacenar la hora tal cual (sin conversión a UTC)
        r.ends_at = now
        
        # Calcular precio final con tolerancia y recargos
        total_price, desglose = await _compute_total_price_checkout(r)
        r.total_price = total_price
        
        # Enviar email de checkout en background
        background_tasks.add_task(send_checkout_email, r, total_price, desglose)
    else:
        # No debería llegar aquí, pero por seguridad
        raise HTTPException(
            status_code=400,
            detail=f"Estado {r.status} no permite escaneo de QR"
        )
    
    r.updated_at = now
    await r.save()
    return r

async def list_disponible(limit: int = 100, offset: int = 0) -> List[VisitorReservation]:
    return await VisitorReservation.all().select_related("spot").offset(offset).limit(limit).order_by("-starts_at")

async def list_reservations(limit: int = 100, offset: int = 0) -> List[VisitorReservation]:
    return await VisitorReservation.all().select_related("spot").offset(offset).limit(limit).order_by("-starts_at")

async def list_reservations_by_user_id(user_id: int, limit: int = 100, offset: int = 0) -> List[VisitorReservation]:
    personas = await Persona.filter(usuario_id=user_id, is_active=True).values("casa_interior_link_id")
    
    #print("Personas encontradas para user_id", user_id, ":", personas)
    
    if not personas:
        return []

    casa_link_ids = [persona["casa_interior_link_id"] for persona in personas]
    return await (
        VisitorReservation.filter(casa_interior_torre_link_id__in=casa_link_ids)
        .select_related("spot")
        .offset(offset)
        .limit(limit)
        .order_by("-starts_at")
    )


async def get_reservation(reservation_id: int) -> Optional[VisitorReservation]:
    return await VisitorReservation.get_or_none(id=reservation_id).select_related("spot")

async def cancel_reservation(reservation_id: int) -> bool:
    r = await VisitorReservation.get_or_none(id=reservation_id)
    if not r:
        return False
    r.status = ReservationStatus.CANCELLED
    await r.save()
    return True

async def complete_reservation(reservation_id: int) -> bool:
    r = await VisitorReservation.get_or_none(id=reservation_id)
    if not r:
        return False
    r.status = ReservationStatus.COMPLETED
    await r.save()
    return True
