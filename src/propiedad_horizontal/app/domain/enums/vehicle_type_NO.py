from enum import Enum

class VehicleType(str, Enum):
    CARRO = "carro"
    MOTO = "moto"
    CICLA = "cicla"
    CICLA_ELECTRICA = "cicla electrica"
    PATINETA_ELECTRICA = "patineta electrica"

    def __str__(self) -> str:
        # default string representation should be the raw value
        # so that str(VehicleType.CARRO) == "carro" instead of "VehicleType.CARRO"
        return self.value

    @property
    def label(self) -> str:
        """Human-readable label including emoji useful for emails or UI.

        Extend this mapping when new vehicle types are added. The fallback
        returns ``self.value`` so you always get something sensible.
        """
        labels = {
            VehicleType.CARRO: "🚗 Automóvil",
            VehicleType.MOTO: "🏍️ Moto",
            VehicleType.CICLA: "🚴 Cicla",
            VehicleType.CICLA_ELECTRICA: "🚴‍♀️ Cicla eléctrica",
            VehicleType.PATINETA_ELECTRICA: "🛴 Patineta eléctrica",
        }
        return labels.get(self, self.value)
