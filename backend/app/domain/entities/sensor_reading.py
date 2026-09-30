"""Relevé horodaté des capteurs d'une machine industrielle."""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite

from app.domain.value_objects.machine_id import MachineId


@dataclass(frozen=True)
class SensorReading:
    """Mesures physiques reçues pour une machine à un instant donné."""

    machine_id: MachineId
    recorded_at: datetime
    power_kw: float
    temperature_c: float
    vibration_hz: float
    pressure_bar: float

    def __post_init__(self) -> None:
        readings = (self.power_kw, self.temperature_c, self.vibration_hz, self.pressure_bar)
        if not all(isfinite(value) for value in readings):
            raise ValueError("Les mesures doivent être des nombres finis")
        if min(self.power_kw, self.vibration_hz, self.pressure_bar) < 0:
            raise ValueError("Puissance, vibration et pression doivent être positives ou nulles")
