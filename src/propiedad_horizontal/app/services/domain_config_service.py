from propiedad_horizontal.app.models.domain_config import DomainConfig

async def get_active_domain() -> str:
    config = await DomainConfig.get_or_none(is_active=True)
    return config.domain if config else None

async def get_active_domain_or_default(default_domain: str) -> str:
    config = await DomainConfig.get_or_none(is_active=True)
    return config.domain if config else default_domain

async def list_configs(limit: int = 100, offset: int = 0):
    return await DomainConfig.all().offset(offset).limit(limit)

async def get_by_id(config_id: int):
    return await DomainConfig.get_or_none(id=config_id)

async def create(domain: str, is_active: bool = True):
    existing = await DomainConfig.filter(domain=domain).exists()
    
    if existing:
        raise ValueError(f"Ya existe una configuración con ese nombre de dominio: '{domain}'")
        
    return await DomainConfig.create(domain=domain, is_active=is_active)

async def update(config_id: int, **kwargs):
    config = await get_by_id(config_id)
    if not config:
        return None
    for key, value in kwargs.items():
        setattr(config, key, value)
    await config.save()
    return config