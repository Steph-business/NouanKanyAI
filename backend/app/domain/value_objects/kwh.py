"""Quantité d'énergie non négative mesurée en kilowattheures."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Kwh:
    """Valeur d'énergie en kWh, représentée précisément par Decimal."""

    value: Decimal

    def __post_init__(self) -> None:
        value = Decimal(str(self.value))
        if not value.is_finite() or value < 0:
            raise ValueError("La quantité en kWh doit être finie et positive ou nulle")
        object.__setattr__(self, "value", value)
