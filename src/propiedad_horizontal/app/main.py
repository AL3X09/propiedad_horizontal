from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from propiedad_horizontal.app.core.db import init_tortoise, close_tortoise
from propiedad_horizontal.app.core.config import settings

# ... tus imports de routers ...
from propiedad_horizontal.app.api.users import router as users_router
from propiedad_horizontal.app.api.auth import router as auth_router
from propiedad_horizontal.app.api.parking_spots import router as parking_spots_router
from propiedad_horizontal.app.api.parking_assignments import router as parking_assignments_router
from propiedad_horizontal.app.api.parking_reservations import router as parking_reservations_router
from propiedad_horizontal.app.api.propiedades_horizontales import router as ph_router
from propiedad_horizontal.app.api.personas import router as personas_router
from propiedad_horizontal.app.api.torres_interiores import router as torres_interiores_router
from propiedad_horizontal.app.api.casas_apartamentos import router as casas_apartamentos_router
from propiedad_horizontal.app.api.casa_interior_links import router as casa_interior_links_router
from propiedad_horizontal.app.api.permissions import router as permissions_router
from propiedad_horizontal.app.api.roles import router as roles_router
from propiedad_horizontal.app.api.parking_lottery import router as parking_lottery_router
from propiedad_horizontal.app.api.vehicle_types import router as vehicle_types_router
from propiedad_horizontal.app.api.vehicles import router as vehicles_router
from propiedad_horizontal.app.api.bienes import router as bienes_router
from propiedad_horizontal.app.api.trasteos import router as trasteos_router
from propiedad_horizontal.app.api.public import router as public_router
from propiedad_horizontal.app.api.notifications import router as notifications_router
from propiedad_horizontal.app.api.domain_config import router as domain_config_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ──────────────────────────────
    await init_tortoise()                          # 1. Conecta la BD

    from propiedad_horizontal.app.models.role import Role
    from propiedad_horizontal.app.models.user import User
    from propiedad_horizontal.app.models.permission import Permission
    from propiedad_horizontal.app.models.vehicle_type import VehicleType
    from propiedad_horizontal.app.models.bien import Bien
    
    await Role.seed_defaults()
    await User.seed_defaults()
    await Permission.seed_defaults()
    await VehicleType.seed_defaults()             # 2. Seed (BD ya disponible)
    await Bien.seed_defaults()
    

    yield  # ◀ la app corre aquí

    # ── SHUTDOWN ─────────────────────────────
    await close_tortoise()                         # 3. Cierra conexiones limpiamente


def generate_custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        contact={
            "name": settings.APP_CONTACT_NAME,
            "email": settings.APP_CONTACT_EMAIL,
        },
        license_info={
            "name": settings.APP_LICENSE,
        },
        terms_of_service=settings.APP_TERMS_OF_SERVICE,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        lifespan=lifespan,
        redirect_slashes=False,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.openapi = lambda: generate_custom_openapi(app)

    #@app.get("/health", tags=["health"])
    #async def health():
    #    return {"status": "ok"}

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(parking_spots_router)
    app.include_router(parking_assignments_router)
    app.include_router(parking_reservations_router)
    app.include_router(ph_router)
    app.include_router(personas_router)
    app.include_router(torres_interiores_router)
    app.include_router(casas_apartamentos_router)
    app.include_router(casa_interior_links_router)
    app.include_router(permissions_router)
    app.include_router(roles_router)
    app.include_router(parking_lottery_router)
    app.include_router(vehicle_types_router)
    app.include_router(vehicles_router)
    app.include_router(bienes_router)
    app.include_router(trasteos_router)
    app.include_router(public_router)
    app.include_router(notifications_router)
    app.include_router(domain_config_router)

    return app


app = create_app()