"""Entité métier représentant une machine industrielle supervisée."""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite

from app.domain.value_objects.machine_id import MachineId


@dataclass(frozen=True)
class Machine:
    """Machine équipée de capteurs et soumise à une puissance maximale."""

    id: MachineId
    name: str
    location: str
    max_power_kw: float
    is_active: bool = True
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.location.strip():
            raise ValueError("Le nom et l'emplacement de la machine sont obligatoires")
        if not isfinite(self.max_power_kw) or self.max_power_kw <= 0:
            raise ValueError("La puissance maximale doit être positive")

    def can_consume(self, requested_kw: float) -> bool:
        """Indique si la machine active peut fournir la puissance demandée."""
        return 0 <= requested_kw <= self.max_power_kw and self.is_active

    def is_overloaded(self, current_kw: float) -> bool:
        """Détecte une surcharge supérieure à 90 % de la puissance maximale."""
        return current_kw > 0.9 * self.max_power_kw
