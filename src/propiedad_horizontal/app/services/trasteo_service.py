from typing import List, Optional
from datetime import datetime
from propiedad_horizontal.app.models.trasteo import Trasteo
from propiedad_horizontal.app.models.trasteo_bien import TrasteoBien
from propiedad_horizontal.app.models.bien import Bien
from propiedad_horizontal.app.models.user import User
from propiedad_horizontal.app.schemas.trasteo import TrasteoCreate, TrasteoUpdate, TrasteoBienCreate


async def create_trasteo(data: TrasteoCreate) -> Trasteo:
    """Crear un nuevo trasteo con su listado de bienes"""
    
    # Verificar que el usuario existe
    usuario = await User.get_or_none(id=data.usuario_id)
    if not usuario:
        raise ValueError(f"Usuario con ID {data.usuario_id} no existe")
    
    # Verificar que todos los bienes existen
    bien_ids = [b.bien_id for b in data.bienes]
    for bien_id in bien_ids:
        bien = await Bien.get_or_none(id=bien_id)
        if not bien:
            raise ValueError(f"Bien con ID {bien_id} no existe")
    
    # Crear el trasteo
    trasteo = await Trasteo.create(
        usuario_id=data.usuario_id,
        fecha_ingreso=data.fecha_ingreso,
        fecha_salida=data.fecha_salida,
        is_autorizado=data.is_autorizado,
    )
    
    # Crear las relaciones Trasteo-Bien
    for bien_data in data.bienes:
        await TrasteoBien.create(
            trasteo_id=trasteo.id,
            bien_id=bien_data.bien_id,
            cantidad=bien_data.cantidad,
        )
    
    return await get_trasteo(trasteo.id)


async def list_trasteos(
    usuario_id: Optional[int] = None,
    is_autorizado: Optional[bool] = None,
    include_inactive: bool = False,
    limit: int = 100,
    offset: int = 0,
) -> List[Trasteo]:
    """Listar trasteos con filtros opcionales"""
    
    query = Trasteo.all()
    
    if not include_inactive:
        query = query.filter(is_active=True)
    
    if usuario_id is not None:
        query = query.filter(usuario_id=usuario_id)
    
    if is_autorizado is not None:
        query = query.filter(is_autorizado=is_autorizado)
    
    return await query.offset(offset).limit(limit).order_by("-fecha_ingreso")


async def get_trasteo(trasteo_id: int) -> Optional[Trasteo]:
    """Obtener un trasteo con sus bienes relacionados"""
    trasteo = await Trasteo.get_or_none(id=trasteo_id)
    if trasteo:
        # Precarga los bienes relacionados
        await trasteo.fetch_related("bienes", "usuario")
    return trasteo


async def get_trasteo_with_bienes(trasteo_id: int) -> Optional[dict]:
    """Obtener un trasteo con detalles completos de bienes"""
    trasteo = await get_trasteo(trasteo_id)
    if not trasteo:
        return None
    
    # Obtener detalles de los bienes
    bienes_trasteo = await TrasteoBien.filter(trasteo_id=trasteo_id).prefetch_related("bien")
    
    bienes_detail = []
    for tb in bienes_trasteo:
        bien = tb.bien
        bienes_detail.append({
            "id": tb.id,
            "bien_id": tb.bien_id,
            "bien_tipo": bien.tipo,
            "bien_descripcion": bien.descripcion,
            "cantidad": tb.cantidad,
            "created_at": tb.created_at,
            "updated_at": tb.updated_at,
        })
    
    return {
        "trasteo": trasteo,
        "bienes": bienes_detail,
    }


async def update_trasteo(trasteo_id: int, data: TrasteoUpdate) -> Optional[Trasteo]:
    """Actualizar un trasteo y opcionalmente sus bienes"""
    
    trasteo = await Trasteo.get_or_none(id=trasteo_id)
    if not trasteo:
        return None
    
    # Actualizar campos escalares
    if data.usuario_id is not None:
        # Verificar que el usuario existe
        usuario = await User.get_or_none(id=data.usuario_id)
        if not usuario:
            raise ValueError(f"Usuario con ID {data.usuario_id} no existe")
        trasteo.usuario_id = data.usuario_id
    
    if data.fecha_ingreso is not None:
        trasteo.fecha_ingreso = data.fecha_ingreso
    
    if data.fecha_salida is not None:
        trasteo.fecha_salida = data.fecha_salida
    
    if data.is_autorizado is not None:
        trasteo.is_autorizado = data.is_autorizado
    
    if data.is_active is not None:
        trasteo.is_active = data.is_active
    
    await trasteo.save()
    
    # Si se envía lista de bienes, reemplazar completamente
    if data.bienes is not None:
        # Eliminar bienes previos
        await TrasteoBien.filter(trasteo_id=trasteo_id).delete()
        
        # Verificar que todos los bienes existen
        for bien_data in data.bienes:
            bien = await Bien.get_or_none(id=bien_data.bien_id)
            if not bien:
                raise ValueError(f"Bien con ID {bien_data.bien_id} no existe")
        
        # Crear nuevas relaciones
        for bien_data in data.bienes:
            await TrasteoBien.create(
                trasteo_id=trasteo_id,
                bien_id=bien_data.bien_id,
                cantidad=bien_data.cantidad,
            )
    
    return await get_trasteo(trasteo_id)


async def delete_trasteo(trasteo_id: int) -> bool:
    """Eliminar (soft delete) un trasteo"""
    trasteo = await Trasteo.get_or_none(id=trasteo_id)
    if not trasteo:
        return False
    
    trasteo.is_active = False
    await trasteo.save()
    return True


async def add_bien_to_trasteo(trasteo_id: int, bien_data: TrasteoBienCreate) -> Optional[TrasteoBien]:
    """Agregar un bien a un trasteo existente"""
    
    trasteo = await Trasteo.get_or_none(id=trasteo_id)
    if not trasteo:
        return None
    
    bien = await Bien.get_or_none(id=bien_data.bien_id)
    if not bien:
        raise ValueError(f"Bien con ID {bien_data.bien_id} no existe")
    
    # Verificar si el bien ya existe en el trasteo
    existing = await TrasteoBien.get_or_none(trasteo_id=trasteo_id, bien_id=bien_data.bien_id)
    if existing:
        raise ValueError(f"El bien {bien_data.bien_id} ya existe en el trasteo {trasteo_id}")
    
    trasteo_bien = await TrasteoBien.create(
        trasteo_id=trasteo_id,
        bien_id=bien_data.bien_id,
        cantidad=bien_data.cantidad,
    )
    
    return trasteo_bien


async def update_trasteo_bien_cantidad(trasteo_bien_id: int, nueva_cantidad: int) -> Optional[TrasteoBien]:
    """Actualizar la cantidad de un bien en un trasteo"""
    
    if nueva_cantidad < 1:
        raise ValueError("La cantidad debe ser mayor o igual a 1")
    
    trasteo_bien = await TrasteoBien.get_or_none(id=trasteo_bien_id)
    if not trasteo_bien:
        return None
    
    trasteo_bien.cantidad = nueva_cantidad
    await trasteo_bien.save()
    
    return trasteo_bien


async def remove_bien_from_trasteo(trasteo_bien_id: int) -> bool:
    """Eliminar un bien de un trasteo"""
    
    trasteo_bien = await TrasteoBien.get_or_none(id=trasteo_bien_id)
    if not trasteo_bien:
        return False
    
    await trasteo_bien.delete()
    return True


async def authorize_trasteo(trasteo_id: int) -> Optional[Trasteo]:
    """Autorizar un trasteo"""
    
    trasteo = await Trasteo.get_or_none(id=trasteo_id)
    if not trasteo:
        return None
    
    trasteo.is_autorizado = True
    await trasteo.save()
    
    return await get_trasteo(trasteo_id)


async def get_bienes_by_usuario(usuario_id: int) -> List[dict]:
    """Obtener todos los bienes de un usuario a través de sus trasteos activos"""
    
    # Obtener todos los trasteos activos del usuario
    trasteos = await Trasteo.filter(usuario_id=usuario_id, is_active=True)
    
    bienes_map = {}  # usar dict para agrupar bienes por tipo y sumar cantidades
    
    for trasteo in trasteos:
        trasteo_bienes = await TrasteoBien.filter(trasteo_id=trasteo.id).prefetch_related("bien")
        
        for tb in trasteo_bienes:
            bien = tb.bien
            key = bien.id
            
            if key not in bienes_map:
                bienes_map[key] = {
                    "bien_id": bien.id,
                    "tipo": bien.tipo,
                    "descripcion": bien.descripcion,
                    "cantidad_total": 0,
                    "trasteos_count": 0,
                }
            
            bienes_map[key]["cantidad_total"] += tb.cantidad
            bienes_map[key]["trasteos_count"] += 1
    
    return list(bienes_map.values())
