from enum import Enum

class ParkingSpotStatus(str, Enum):
    AVIABLE = "disponible"
    BUSY = "ocupado"
