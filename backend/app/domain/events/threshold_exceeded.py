"""Événement métier indiquant le dépassement d'un seuil énergétique."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.value_objects.machine_id import MachineId


@dataclass(frozen=True)
class ThresholdExceeded:
    """Fait métier indiquant une valeur au-dessus du seuil défini."""

    machine_id: MachineId
    metric: str
    observed_value: float
    threshold: float
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
