from typing import List, Optional
from tortoise.exceptions import IntegrityError
from propiedad_horizontal.app.models.casa_apartamento import CasaApartamento
from propiedad_horizontal.app.schemas.casa_apartamento import CasaApartamentoCreate, CasaApartamentoUpdate

async def create_casa_apartamento(data: CasaApartamentoCreate) -> CasaApartamento:
    try:
        item = await CasaApartamento.create(c_numero_letra=data.c_numero_letra.strip())
        return item
    except IntegrityError:
        raise ValueError("Ya existe un registro con ese número.")

async def list_casas_apartamentos(
    q: Optional[str] = None,  # filtro por substring del número
    active_only: bool = True,
    limit: int = 100,
    offset: int = 0,
) -> List[CasaApartamento]:
    qs = CasaApartamento.all().order_by("c_numero_letra")
    if q:
        qs = qs.filter(c_numero_letra__icontains=q)
    if active_only:
        qs = qs.filter(is_active=True)
    return await qs.offset(offset).limit(limit)

async def get_casa_apartamento(item_id: int) -> Optional[CasaApartamento]:
    return await CasaApartamento.get_or_none(id=item_id)

async def get_id_casa_apartammento(c_numero_letra: str) -> Optional[int]:
    obj = await CasaApartamento.get_or_none(c_numero_letra=c_numero_letra)
    return obj.id if obj else None

async def update_casa_apartamento(item_id: int, data: CasaApartamentoUpdate) -> Optional[CasaApartamento]:
    item = await CasaApartamento.get_or_none(id=item_id)
    if not item:
        return None
    if data.c_numero_letra is not None:
        item.c_numero_letra = data.c_numero_letra.strip()
    if data.is_active is not None:
        item.is_active = data.is_active
    try:
        await item.save()
        return item
    except IntegrityError:
        raise ValueError("El número ya está en uso.")

async def deactivate_casa_apartamento(item_id: int) -> bool:
    item = await CasaApartamento.get_or_none(id=item_id)
    if not item:
        return False
    item.is_active = False
    await item.save()
    return True
