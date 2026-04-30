from enum import Enum

class LotteryStatus(str, Enum):
    """Estado del sorteo de parqueaderos"""
    PENDING = "pending"       # Sorteo pendiente de ejecutar
    IN_PROGRESS = "in_progress"  # Sorteo en proceso
    COMPLETED = "completed"   # Sorteo completado
    CANCELLED = "cancelled"   # Sorteo cancelado


class LotteryParticipantStatus(str, Enum):
    """Estado del participante en el sorteo"""
    ELIGIBLE = "eligible"           # Elegible para participar
    EXCLUDED_TEMPORARILY = "excluded_temporarily"  # Excluido temporalmente (por 6 meses consecutivos)
    EXCLUDED_THIS_ROUND = "excluded_this_round"    # Excluido solo en esta ronda
    SELECTED = "selected"           # Seleccionado en el sorteo
    NOT_SELECTED = "not_selected"  # No seleccionado
    WAITING_LIST = "waiting_list"  # En lista de espera
