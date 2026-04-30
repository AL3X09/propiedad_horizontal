from typing import List, Optional
from tortoise.exceptions import IntegrityError
from propiedad_horizontal.app.models.torre_interior import TorreInterior
from propiedad_horizontal.app.schemas.torre_interior import TorreInteriorCreate, TorreInteriorUpdate

async def create_torre_interior(data: TorreInteriorCreate) -> TorreInterior:
    try:
        ti = await TorreInterior.create(
            t_numero_letra=data.t_numero_letra.strip(),
        )
        return ti
    except IntegrityError:
        # Violación de unique (t_numero_letra global)
        raise ValueError("Ya existe una torre interior con ese t_numero_letra.")

async def list_torres_interiores(
    q: Optional[str] = None,  # filtro por substring de t_numero_letra
    active_only: bool = True,
    limit: int = 100,
    offset: int = 0,
) -> List[TorreInterior]:
    qs = TorreInterior.all().order_by("t_numero_letra")
    if q:
        qs = qs.filter(t_numero_letra__icontains=q)
    if active_only:
        qs = qs.filter(is_active=True)
    return await qs.offset(offset).limit(limit)

async def get_torre_interior(torre_interior_id: int) -> Optional[TorreInterior]:
    return await TorreInterior.get_or_none(id=torre_interior_id)

async def get_id_torre_interior(num_torre_interior: str) -> Optional[int]:
    obj = await TorreInterior.get_or_none(t_numero_letra=num_torre_interior)
    return obj.id if obj else None

async def update_torre_interior(torre_interior_id: int, data: TorreInteriorUpdate) -> Optional[TorreInterior]:
    ti = await TorreInterior.get_or_none(id=torre_interior_id)
    if not ti:
        return None
    if data.t_numero_letra is not None:
        ti.t_numero_letra = data.t_numero_letra.strip()
    if data.is_active is not None:
        ti.is_active = data.is_active
    try:
        await ti.save()
        return ti
    except IntegrityError:
        raise ValueError("El t_numero_letra ya está en uso.")

async def deactivate_torre_interior(torre_interior_id: int) -> bool:
    ti = await TorreInterior.get_or_none(id=torre_interior_id)
    if not ti:
        return False
    ti.is_active = False
    await ti.save()
    return True
