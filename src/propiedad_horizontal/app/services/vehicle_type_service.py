from typing import List, Optional
from propiedad_horizontal.app.models.vehicle_type import VehicleType
from propiedad_horizontal.app.schemas.vehicle_type import (
    VehicleTypeCreate,
    VehicleTypeUpdate,
    VehicleTypeRead,
    VehicleTypeToggle,
)


async def create_vehicle_type(data: VehicleTypeCreate) -> VehicleType:
    """
    Crea un nuevo tipo de vehículo.
    El código debe ser único.
    """
    existing = await VehicleType.filter(name=data.name).exists()
    if existing:
        raise ValueError(f"Ya existe un tipo de vehículo con nombre '{data.name}'")

    vt = await VehicleType.create(
        name=data.name,
        emoji=data.emoji,
        description=data.description,
        display_order=data.display_order,
    )
    return vt


async def list_vehicle_types(
    include_inactive: bool = False,
    limit: int = 100,
    offset: int = 0,
) -> List[VehicleType]:
    """
    Lista tipos de vehículos.
    Si include_inactive=True, incluye los inactivos.
    """
    q = VehicleType.all()
    if not include_inactive:
        q = q.filter(is_active=True)
    return await q.offset(offset).limit(limit).order_by("display_order")


async def get_vehicle_type(vt_id: int) -> Optional[VehicleType]:
    """Obtiene un tipo de vehículo por ID."""
    return await VehicleType.get_or_none(id=vt_id)


async def update_vehicle_type(
    vt_id: int,
    data: VehicleTypeUpdate,
) -> Optional[VehicleType]:
    """
    Actualiza un tipo de vehículo.
    Retorna None si no existe.
    """
    vt = await VehicleType.get_or_none(id=vt_id)
    if not vt:
        return None

    if data.name is not None:
        vt.name = data.name
    if data.emoji is not None:
        vt.emoji = data.emoji
    if data.description is not None:
        vt.description = data.description
    if data.display_order is not None:
        vt.display_order = data.display_order

    await vt.save()
    return vt


async def toggle_vehicle_type(vt_id: int, is_active: bool) -> Optional[VehicleType]:
    """
    Activa o desactiva un tipo de vehículo (soft-delete).
    Retorna None si no existe.
    """
    vt = await VehicleType.get_or_none(id=vt_id)
    if not vt:
        return None

    vt.is_active = is_active
    await vt.save()
    return vt


async def delete_vehicle_type(vt_id: int) -> bool:
    """
    Desactiva un tipo de vehículo (soft-delete).
    Retorna True si existía y False si no.
    """
    vt = await VehicleType.get_or_none(id=vt_id)
    if not vt:
        return False

    vt.is_active = False
    await vt.save()
    return True


async def get_active_vehicle_types() -> List[VehicleType]:
    """
    Obtiene solo los tipos de vehículo activos.
    Útil para poblar selects en UI.
    """
    return await VehicleType.filter(is_active=True).order_by("display_order")