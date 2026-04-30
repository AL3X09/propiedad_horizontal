from enum import Enum

class ReservationStatus(str, Enum):
    ACTIVE = "activa" #cuando la reserva está vigente y el visitante no ha llegado aún
    COMPLETED = "completada" # cuando un visitante llega a tomar la reserva del parqueadero
    CANCELLED = "cancelada" #cuando se anula la reserva antes de usar el parqueadero
    FINISHED = "finalizada" #cuando el visitante ya se fue y libera el parqueadero
    VIOLATED = "incumplida" #cuando el visitante ya se fue y libera el parqueadero