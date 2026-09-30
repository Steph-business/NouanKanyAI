"""Événement émis lorsqu'une mesure est classée comme anomalie."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.value_objects.machine_id import MachineId


@dataclass(frozen=True)
class AnomalyDetected:
    """Fait métier signalant une anomalie détectée sur une machine."""

    machine_id: MachineId
    severity: str
    score: float
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
