from typing import List, Optional
from propiedad_horizontal.app.models.bien import Bien
from propiedad_horizontal.app.schemas.bien import BienCreate, BienUpdate

async def create_bien(data: BienCreate) -> Bien:
    bien = await Bien.create(
        tipo=data.tipo,
        descripcion=data.descripcion,
    )

    return await Bien.filter(id=bien.id).first()


async def list_bienes(
    tipo: Optional[str] = None,
    include_inactive: bool = False,
    limit: int = 100,
    offset: int = 0,
) -> List[Bien]:
    query = Bien.all()
    if not include_inactive:
        query = query.filter(is_active=True)
    if tipo is not None:
        query = query.filter(tipo__icontains=tipo)
    return await query.offset(offset).limit(limit).order_by("-created_at")


async def get_bien(bien_id: int) -> Optional[Bien]:
    return await Bien.filter(id=bien_id).first()


async def update_bien(bien_id: int, data: BienUpdate) -> Optional[Bien]:
    bien = await Bien.get_or_none(id=bien_id)
    if not bien:
        return None

    if data.tipo is not None:
        bien.tipo = data.tipo
    if data.descripcion is not None:
        bien.descripcion = data.descripcion
    if data.is_active is not None:
        bien.is_active = data.is_active

    await bien.save()

    return await Bien.filter(id=bien_id).first()


async def toggle_bien(bien_id: int, is_active: bool) -> Optional[Bien]:
    bien = await Bien.get_or_none(id=bien_id)
    if not bien:
        return None
    bien.is_active = is_active
    await bien.save()
    return await Bien.filter(id=bien_id).first()


async def delete_bien(bien_id: int) -> bool:
    bien = await Bien.get_or_none(id=bien_id)
    if not bien:
        return False
    bien.is_active = False
    await bien.save()
    return True
