from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    OWNER = "propietario"
    TENANT = "arrendatario"
    WATCHMAN = "celador"
    CLEANER = "aseador"
    HANDYMAN = "todero"
    COUNSELOR = "consejero"
    ADMINISTRATOR = "administrador"
    