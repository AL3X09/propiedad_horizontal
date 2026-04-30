from typing import List, Optional
from tortoise.exceptions import IntegrityError
from propiedad_horizontal.app.models.parking import ParkingSpot
from propiedad_horizontal.app.models.vehicle_type import VehicleType
from propiedad_horizontal.app.domain.enums import ParkingSpotStatus
from propiedad_horizontal.app.schemas.parking import ParkingSpotCreate, ParkingSpotUpdate

async def create_spot(data: ParkingSpotCreate) -> ParkingSpot:
    # Validar que el tipo de vehículo existe y está activo
    vehicle_type = await VehicleType.get_or_none(id=data.vehicle_type_id, is_active=True)
    if not vehicle_type:
        raise ValueError("Tipo de vehículo no encontrado o inactivo.")
    try:
        spot = await ParkingSpot.create(
            code=data.code,
            vehicle_type_id=data.vehicle_type_id,
            monthly_price=data.monthly_price,
            minute_price=data.minute_price,
        )
        return spot
    except IntegrityError:
        raise ValueError("El código de parqueadero ya existe.")

async def list_spots(vehicle_type_id: int | None, parking_status: ParkingSpotStatus | None, is_parking_public: bool | None, active_only: bool = True, limit: int = 100, offset: int = 0) -> List[ParkingSpot]:
    qs = ParkingSpot.all()
    if active_only:
        qs = qs.filter(is_active=True)
    if vehicle_type_id is not None:
        qs = qs.filter(vehicle_type_id=vehicle_type_id)
    if parking_status is not None:
        qs = qs.filter(parking_status=parking_status)
    if is_parking_public is not None:
        qs = qs.filter(is_parking_public=is_parking_public)
    return await qs.offset(offset).limit(limit).order_by("code")

async def get_spot(spot_id: int) -> Optional[ParkingSpot]:
    return await ParkingSpot.get_or_none(id=spot_id)

async def update_spot(spot_id: int, data: ParkingSpotUpdate) -> Optional[ParkingSpot]:
    spot = await ParkingSpot.get_or_none(id=spot_id)
    if not spot:
        return None
    if data.vehicle_type_id is not None:
        spot.vehicle_type_id = data.vehicle_type_id
    if data.monthly_price is not None:
        spot.monthly_price = data.monthly_price
    if data.minute_price is not None:
        spot.minute_price = data.minute_price
    if data.is_active is not None:
        spot.is_active = data.is_active
    if data.is_parking_public is not None:
        spot.is_parking_public = data.is_parking_public
    await spot.save()
    return spot

async def deactivate_spot(spot_id: int) -> bool:
    spot = await ParkingSpot.get_or_none(id=spot_id)
    if not spot:
        return False
    spot.is_active = False
    await spot.save()
    return True
