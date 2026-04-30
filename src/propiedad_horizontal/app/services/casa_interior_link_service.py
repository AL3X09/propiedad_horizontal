from typing import List, Optional
from tortoise.exceptions import IntegrityError
from propiedad_horizontal.app.models.casa_apartamento_interior_torre import CasaApartamentoInteriorTorre
from propiedad_horizontal.app.models.casa_apartamento import CasaApartamento
from propiedad_horizontal.app.models.torre_interior import TorreInterior
from propiedad_horizontal.app.schemas.casa_interior_link import CasaInteriorLinkCreate, CasaInteriorLinkUpdate
from propiedad_horizontal.app.domain.enums import ApartmentStatus

async def _validate_sides(casa_id: int, interior_id: int) -> None:
    casa = await CasaApartamento.get_or_none(id=casa_id)
    if not casa or not casa.is_active:
        raise ValueError("CasaApartamento no existe o está inactiva.")
    interior = await TorreInterior.get_or_none(id=interior_id)
    if not interior or not interior.is_active:
        raise ValueError("TorreInterior no existe o está inactiva.")

async def create_link(data: CasaInteriorLinkCreate) -> CasaApartamentoInteriorTorre:
    await _validate_sides(data.casa_apartamento_id, data.torre_interior_id)
    try:
        link = await CasaApartamentoInteriorTorre.create(
            casa_apartamento_id=data.casa_apartamento_id,
            torre_interior_id=data.torre_interior_id,
            status=data.status,
            num_habitaciones=data.num_habitaciones,
        )
        return await CasaApartamentoInteriorTorre.get_or_none(id=link.id).select_related(
            "casa_apartamento", "torre_interior"
        )
    except IntegrityError:
        # Duplicado por unique_together
        raise ValueError("Ya existe el vínculo entre esa CasaApartamento y esa TorreInterior.")

async def list_links(
    casa_apartamento_id: Optional[int] = None,
    torre_interior_id: Optional[int] = None,
    status: Optional[ApartmentStatus] = None,
    active_only: bool = True,
    limit: int = 100,
    offset: int = 0,
) -> List[CasaApartamentoInteriorTorre]:
    qs = CasaApartamentoInteriorTorre.all().select_related("casa_apartamento", "torre_interior").order_by("id")
    if casa_apartamento_id is not None:
        qs = qs.filter(casa_apartamento_id=casa_apartamento_id)
    if torre_interior_id is not None:
        qs = qs.filter(torre_interior_id=torre_interior_id)
    if status is not None:
        qs = qs.filter(status=status)
    if active_only:
        qs = qs.filter(is_active=True)
    return await qs.offset(offset).limit(limit)

async def get_link(link_id: int) -> Optional[CasaApartamentoInteriorTorre]:
    return await CasaApartamentoInteriorTorre.get_or_none(id=link_id).select_related("casa_apartamento", "torre_interior")

async def get_torrecasa_id(id_casa_apto: int, id_interior_torre: int) -> Optional[int]:
    obj = await CasaApartamentoInteriorTorre.get_or_none(
        casa_apartamento_id=id_casa_apto,
        torre_interior_id=id_interior_torre
    )
    return obj.id if obj else None

async def update_link(link_id: int, data: CasaInteriorLinkUpdate) -> Optional[CasaApartamentoInteriorTorre]:
    link = await CasaApartamentoInteriorTorre.get_or_none(id=link_id)
    if not link:
        return None
    if data.status is not None:
        link.status = data.status
    if data.num_habitaciones is not None:
        link.num_habitaciones = data.num_habitaciones
    if data.is_active is not None:
        link.is_active = data.is_active
    await link.save()
    return await CasaApartamentoInteriorTorre.get_or_none(id=link_id).select_related(
        "casa_apartamento", "torre_interior"
    )

async def deactivate_link(link_id: int) -> bool:
    link = await CasaApartamentoInteriorTorre.get_or_none(id=link_id)
    if not link:
        return False
    link.is_active = False
    await link.save()
    return True
