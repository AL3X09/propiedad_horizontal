from pydantic import BaseModel, ConfigDict, Field
from datetime import date
# Los precios se almacenan como string (CharField) en el modelo, por lo tanto el schema usa str
# from decimal import Decimal  # ya no se requiere Decimal
from propiedad_horizontal.app.domain.enums import AssignmentStatus

class MonthlyAssignmentCreate(BaseModel):
    spot_id: int
    persona_id: int  # ID de la persona asignataria del parqueadero
    start_date: date
    months: int = Field(ge=1, le=6)
    vehicle_type_id: int

class MonthlyAssignmentRead(BaseModel):
    id: int
    spot_id: int
    persona_id: int  # ID de la persona asignataria
    start_date: date
    months: int
    end_date: date
    vehicle_type_id: int
    status: AssignmentStatus
    monthly_price: str  # tipo string para coincidir con CharField del modelo
    total_price: str   # tipo string para coincidir con CharField del modelo

    model_config = ConfigDict(from_attributes=True)
