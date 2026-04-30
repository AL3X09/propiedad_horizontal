from pydantic import BaseModel, ConfigDict
from propiedad_horizontal.app.domain.enums import ParkingSpotStatus


class ParkingSpotCreate(BaseModel):
    code: str
    vehicle_type_id: int
    monthly_price: str
    minute_price: str


class ParkingSpotUpdate(BaseModel):
    vehicle_type_id: int | None = None
    parking_status: ParkingSpotStatus | None = None
    monthly_price: str | None = None
    minute_price: str | None = None
    is_active: bool | None = None
    is_parking_public: bool | None = None


class ParkingSpotRead(BaseModel):
    id: int
    code: str
    vehicle_type_id: int
    parking_status: ParkingSpotStatus
    is_active: bool
    is_parking_public: bool
    monthly_price: str
    minute_price: str

    model_config = ConfigDict(from_attributes=True)
