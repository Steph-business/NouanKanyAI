"""Consommation énergétique d'une machine sur une période définie."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.value_objects.kwh import Kwh
from app.domain.value_objects.machine_id import MachineId
from app.domain.value_objects.money import Money


@dataclass(frozen=True)
class EnergyConsumption:
    """Consommation et coût associés à une machine et à une période."""

    machine_id: MachineId
    period_start: datetime
    period_end: datetime
    energy: Kwh
    cost: Money

    def __post_init__(self) -> None:
        if self.period_end <= self.period_start:
            raise ValueError("La fin de période doit suivre son début")
