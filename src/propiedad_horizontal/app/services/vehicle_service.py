from typing import List, Optional
from propiedad_horizontal.app.models.vehicle import Vehicle
from propiedad_horizontal.app.models.persona import Persona
from propiedad_horizontal.app.models.vehicle_type import VehicleType
from propiedad_horizontal.app.schemas.vehicle import (
    VehicleCreate,
    VehicleUpdate,
    VehicleRead,
    VehicleToggle,
)


async def _validate_persona(persona_id: int) -> int:
    """
    Valida que la persona existe y está activa.
    """
    persona = await Persona.get_or_none(id=persona_id, is_active=True)
    if not persona:
        raise ValueError("La persona no existe o está inactiva.")
    return persona_id


async def _validate_vehicle_type(vehicle_type_id: int) -> int:
    """
    Valida que el tipo de vehículo existe y está activo.
    """
    vt = await VehicleType.get_or_none(id=vehicle_type_id, is_active=True)
    if not vt:
        raise ValueError("El tipo de vehículo no existe o está inactivo.")
    return vehicle_type_id


async def create_vehicle(data: VehicleCreate) -> Vehicle:
    """
    Crea un nuevo vehículo.
    La placa debe ser única.
    """
    existing = await Vehicle.filter(placa_code=data.placa_code).exists()
    if existing:
        raise ValueError(f"Ya existe un vehículo con placa '{data.placa_code}'")

    await _validate_persona(data.persona_id)
    await _validate_vehicle_type(data.vehicle_type_id)

    vehicle = await Vehicle.create(
        persona_id=data.persona_id,
        vehicle_type_id=data.vehicle_type_id,
        placa_code=data.placa_code.upper(),
    )
    return vehicle


async def list_vehicles(
    persona_id: Optional[int] = None,
    vehicle_type_id: Optional[int] = None,
    include_inactive: bool = False,
    limit: int = 100,
    offset: int = 0,
) -> List[Vehicle]:
    """
    Lista vehículos.
    Si include_inactive=True, incluye los inactivos.
    """
    q = Vehicle.all()
    if not include_inactive:
        q = q.filter(is_active=True)
    if persona_id is not None:
        q = q.filter(persona_id=persona_id)
    if vehicle_type_id is not None:
        q = q.filter(vehicle_type_id=vehicle_type_id)
    return await q.offset(offset).limit(limit).order_by("-created_at")


async def get_vehicle(vehicle_id: int) -> Optional[Vehicle]:
    """Obtiene un vehículo por ID."""
    return await Vehicle.get_or_none(id=vehicle_id).select_related("persona", "vehicle_type")


async def get_vehicle_by_placa(placa_code: str) -> Optional[Vehicle]:
    """Obtiene un vehículo por su placa."""
    return await Vehicle.get_or_none(placa_code=placa_code.upper()).select_related("persona", "vehicle_type")


async def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
) -> Optional[Vehicle]:
    """
    Actualiza un vehículo.
    Retorna None si no existe.
    """
    vehicle = await Vehicle.get_or_none(id=vehicle_id)
    if not vehicle:
        return None

    if data.persona_id is not None:
        await _validate_persona(data.persona_id)
        vehicle.persona_id = data.persona_id
    if data.vehicle_type_id is not None:
        await _validate_vehicle_type(data.vehicle_type_id)
        vehicle.vehicle_type_id = data.vehicle_type_id
    if data.placa_code is not None:
        existing = await Vehicle.filter(placa_code=data.placa_code.upper()).exclude(id=vehicle_id).exists()
        if existing:
            raise ValueError(f"Ya existe un vehículo con placa '{data.placa_code}'")
        vehicle.placa_code = data.placa_code.upper()

    await vehicle.save()
    return vehicle


async def toggle_vehicle(vehicle_id: int, is_active: bool) -> Optional[Vehicle]:
    """
    Activa o desactiva un vehículo (soft-delete).
    Retorna None si no existe.
    """
    vehicle = await Vehicle.get_or_none(id=vehicle_id)
    if not vehicle:
        return None

    vehicle.is_active = is_active
    await vehicle.save()
    return vehicle


async def delete_vehicle(vehicle_id: int) -> bool:
    """
    Desactiva un vehículo (soft-delete).
    Retorna True si existía y False si no.
    """
    vehicle = await Vehicle.get_or_none(id=vehicle_id)
    if not vehicle:
        return False

    vehicle.is_active = False
    await vehicle.save()
    return True


async def get_active_vehicles() -> List[Vehicle]:
    """
    Obtiene solo los vehículos activos.
    Útil para poblar selects en UI.
    """
    return await Vehicle.filter(is_active=True).order_by("placa")