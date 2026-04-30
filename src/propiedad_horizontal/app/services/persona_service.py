from typing import List, Optional
from propiedad_horizontal.app.models.persona import Persona
from propiedad_horizontal.app.models.casa_apartamento_interior_torre import CasaApartamentoInteriorTorre
from propiedad_horizontal.app.models.user import User
from propiedad_horizontal.app.schemas.persona import PersonaCreate, PersonaUpdate

# CORRECCIÓN: Ahora se valida el link (casa-torre) en lugar de solo la casa/apartamento
# Esto asegura que la persona esté asociada a una combinación válida casa-torre
async def _validate_casa_interior_link(link_id: int) -> None:
    """
    Valida que el link CasaApartamentoInteriorTorre existe y está activo.
    El link representa la relación entre una casa/apartamento y una torre/interior.
    """
    link = await CasaApartamentoInteriorTorre.get_or_none(id=link_id)
    if not link or not link.is_active:
        raise ValueError("El link casa-interior no existe o está inactivo.")

async def _validate_usuario(usuario_id: Optional[int]) -> Optional[int]:
    if usuario_id is None:
        return None
    user = await User.get_or_none(id=usuario_id)
    if not user or not user.is_active:
        raise ValueError("Usuario no existe o está inactivo.")
    return usuario_id

# CORRECCIÓN: La regla de único propietario ahora aplica por link (casa-torre)
# Esto permite que una misma casa tenga diferentes propietarios en diferentes torres
async def _enforce_single_owner(link_id: int, exclude_persona_id: Optional[int] = None) -> None:
    """
    Regla opcional: máximo 1 propietario ACTIVO por link casa-interior.
    Llama antes de crear/actualizar cuando is_propietario=True y is_active=True.
    """
    qs = Persona.filter(casa_interior_link_id=link_id, is_active=True, is_propietario=True)
    if exclude_persona_id is not None:
        qs = qs.exclude(id=exclude_persona_id)
    if await qs.exists():
        raise ValueError("Ya existe un propietario activo para este link.")

# CORRECCIÓN: La regla de único arrendatario ahora aplica por link (casa-torre)
async def _enforce_single_tenant(link_id: int, exclude_persona_id: Optional[int] = None) -> None:
    """
    Regla opcional: máximo 1 arrendatario ACTIVO por link casa-interior.
    """
    qs = Persona.filter(casa_interior_link_id=link_id, is_active=True, is_arrendatario=True)
    if exclude_persona_id is not None:
        qs = qs.exclude(id=exclude_persona_id)
    if await qs.exists():
        raise ValueError("Ya existe un arrendatario activo para este link.")

async def create_persona(data: PersonaCreate) -> Persona:
    # CORRECCIÓN: Se valida el link en lugar de la casa directamente
    await _validate_casa_interior_link(data.casa_interior_link_id)
    usuario_id = await _validate_usuario(data.usuario_id)

    # Reglas opcionales (actívalas si las necesitas)
    if data.is_propietario and data.acepta_terminosycondiciones and True:
        await _enforce_single_owner(data.casa_interior_link_id)
    if data.is_arrendatario and data.acepta_terminosycondiciones and True:
        await _enforce_single_tenant(data.casa_interior_link_id)

    persona = await Persona.create(
        casa_interior_link_id=data.casa_interior_link_id,
        usuario_id=usuario_id,
        nombres=data.nombres.strip(),
        apellidos=data.apellidos.strip(),
        edad=data.edad,
        celular=(data.celular.strip() if data.celular else None),
        email=(data.email.strip() if data.email else None),
        is_propietario=data.is_propietario,
        is_arrendatario=data.is_arrendatario,
        acepta_terminosycondiciones=data.acepta_terminosycondiciones,
    )
    return persona

async def list_personas(
    casa_interior_link_id: Optional[int] = None,  # CORRECCIÓN: Nuevo parámetro
    usuario_id: Optional[int] = None,
    active_only: bool = True,
    is_propietario: Optional[bool] = None,
    is_arrendatario: Optional[bool] = None,
    nombre_like: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Persona]:
    qs = Persona.all().order_by("apellidos", "nombres")
    # CORRECCIÓN: Filtrar por link en lugar de casa
    if casa_interior_link_id is not None:
        qs = qs.filter(casa_interior_link_id=casa_interior_link_id)
    if usuario_id is not None:
        qs = qs.filter(usuario_id=usuario_id)
    if active_only:
        qs = qs.filter(is_active=True)
    if is_propietario is not None:
        qs = qs.filter(is_propietario=is_propietario)
    if is_arrendatario is not None:
        qs = qs.filter(is_arrendatario=is_arrendatario)
    if nombre_like:
        qs = qs.filter(nombres__icontains=nombre_like) | qs.filter(apellidos__icontains=nombre_like)
    return await qs.offset(offset).limit(limit)

async def get_persona(persona_id: int) -> Optional[Persona]:
    # CORRECCIÓN: Select related ahora usa casa_interior_link en lugar de casa_apartamento
    return await Persona.get_or_none(id=persona_id).select_related("casa_interior_link", "usuario")

async def update_persona(persona_id: int, data: PersonaUpdate) -> Optional[Persona]:
    persona = await Persona.get_or_none(id=persona_id)
    if not persona:
        return None

    # CORRECCIÓN: Se valida el link en lugar de la casa
    target_link_id = data.casa_interior_link_id if data.casa_interior_link_id is not None else persona.casa_interior_link_id
    await _validate_casa_interior_link(target_link_id)

    if data.usuario_id is not None:
        persona.usuario_id = await _validate_usuario(data.usuario_id)

    # Datos
    if data.nombres is not None:
        persona.nombres = data.nombres.strip()
    if data.apellidos is not None:
        persona.apellidos = data.apellidos.strip()
    if data.edad is not None:
        persona.edad = data.edad
    if data.celular is not None:
        persona.celular = data.celular.strip() if data.celular else None
    if data.email is not None:
        persona.email = data.email.strip() if data.email else None
    if data.is_propietario is not None:
        persona.is_propietario = data.is_propietario
    if data.is_arrendatario is not None:
        persona.is_arrendatario = data.is_arrendatario
    if data.acepta_terminosycondiciones is not None:
        persona.acepta_terminosycondiciones = data.acepta_terminosycondiciones
    if data.is_active is not None:
        persona.is_active = data.is_active

    # CORRECCIÓN: Aplicar cambio de link en lugar de casa
    persona.casa_interior_link_id = target_link_id

    # Reglas opcionales (verifica exclusividad si está activo)
    if persona.is_active and persona.acepta_terminosycondiciones:
        if persona.is_propietario:
            await _enforce_single_owner(persona.casa_interior_link_id, exclude_persona_id=persona.id)
        if persona.is_arrendatario:
            await _enforce_single_tenant(persona.casa_interior_link_id, exclude_persona_id=persona.id)

    await persona.save()
    return persona

async def deactivate_persona(persona_id: int) -> bool:
    persona = await Persona.get_or_none(id=persona_id)
    if not persona:
        return False
    persona.is_active = False
    await persona.save()
    return True
