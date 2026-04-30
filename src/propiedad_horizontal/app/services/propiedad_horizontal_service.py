from typing import List, Optional
from tortoise.exceptions import IntegrityError
from propiedad_horizontal.app.models.propiedad_horizontal import PropiedadHorizontal
from propiedad_horizontal.app.schemas.propiedad_horizontal import (
    PropiedadHorizontalCreate, PropiedadHorizontalUpdate
)

async def create_ph(data: PropiedadHorizontalCreate) -> PropiedadHorizontal:
    # Normalizaciones leves (quita espacios)
    payload = data.model_dump()
    for k in ["nombre", "direccion", "telefono", "localidad", "barrio", "correo"]:
        if payload.get(k) is not None and isinstance(payload[k], str):
            payload[k] = payload[k].strip()

    ph = await PropiedadHorizontal.create(**payload)
    return ph

async def list_ph(
    nombre: Optional[str] = None,
    localidad: Optional[str] = None,
    barrio: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[PropiedadHorizontal]:
    qs = PropiedadHorizontal.all().order_by("nombre")
    if nombre:
        qs = qs.filter(nombre__icontains=nombre)
    if localidad:
        qs = qs.filter(localidad__icontains=localidad)
    if barrio:
        qs = qs.filter(barrio__icontains=barrio)
    return await qs.offset(offset).limit(limit)

async def get_ph(ph_id: int) -> Optional[PropiedadHorizontal]:
    return await PropiedadHorizontal.get_or_none(id=ph_id)

async def update_ph(ph_id: int, data: PropiedadHorizontalUpdate) -> Optional[PropiedadHorizontal]:
    ph = await PropiedadHorizontal.get_or_none(id=ph_id)
    if not ph:
        return None

    payload = data.model_dump(exclude_unset=True)
    for k, v in payload.items():
        if isinstance(v, str):
            setattr(ph, k, v.strip())
        else:
            setattr(ph, k, v)

    await ph.save()
    return ph
