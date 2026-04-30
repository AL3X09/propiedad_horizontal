from enum import Enum

class ApartmentStatus(str, Enum):
    EN_PROPIEDAD = "en_propiedad"
    EN_ARRIENDO = "en_arriendo"
    DESHABITADO = "deshabitado"
