from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from propiedad_horizontal.app.domain.enums import ReservationStatus

class VisitorReservationCreate(BaseModel):
    spot_id: int
    casa_apto_interior_torre_id: int
    starts_at: datetime
    ends_at: datetime
    visitor_name: str
    visitor_email: str
    visitor_cell: str
    visitor_type_document: str
    visitor_document_number: str
    vehicle_type_id: int
    vehicle_code: str  # Placa u otro identificador (ej: ABC-123)
    billed_minutes: int
    # no se envía qr_token; se genera automáticamente

class VisitorReservationRead(BaseModel):
    id: int
    spot_id: int
    starts_at: datetime
    ends_at: datetime
    visitor_name: str
    visitor_email: str
    visitor_cell: str
    visitor_type_document: str
    visitor_document_number: str
    vehicle_type_id: int
    vehicle_code: str  # Placa u otro identificador
    billed_minutes: int
    qr_token: str
    #hourly_price: Decimal
    total_price: Decimal
    status: ReservationStatus

class VisitorReservationRead(BaseModel):
    id: int
    spot_id: int
    starts_at: datetime
    ends_at: datetime
    visitor_name: str
    visitor_email: str
    visitor_cell: str
    visitor_type_document: str
    visitor_document_number: str
    vehicle_type_id: int
    vehicle_code: str  # Placa u otro identificador
    billed_minutes: int
    qr_token: str
    #hourly_price: Decimal
    total_price: Decimal
    status: ReservationStatus

    model_config = ConfigDict(from_attributes=True)


class ScanQRResponse(BaseModel):
    """
    Respuesta del escaneo QR con información de éxito/error.
    
    CÓDIGOS DE ÉXITO:
    - 200: Escaneo exitoso
      - ACTIVE → COMPLETED: Visitante llegó al parqueadero (primer escaneo)
      - COMPLETED → FINISHED: Visitante se fue del parqueadero (segundo escaneo)
    
    CÓDIGOS DE ERROR:
    - 400: Validación inválida
    - 401: Token QR inválido
    - 404: Reserva no encontrada
    - 409: Reserva ya está finalizada
    - 410: Reserva cancelada o incumplida (llegó tarde > 10 min)
    """
    status_code: int  # 200 = éxito, 4xx = error
    detail: str  # Mensaje descriptivo del resultado
    data: VisitorReservationRead  # Datos de la reserva actualizada
