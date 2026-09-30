"""Commandes et résultats du use case de diagnostic d'anomalie."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DetectAnomalyCommand:
    """Demande de diagnostic sur les relevés d'une machine."""

    machine_id: str
    start: datetime | None = None
    end: datetime | None = None


@dataclass(frozen=True)
class DetectAnomalyResult:
    """Diagnostic métier produit à partir des relevés récents."""

    machine_id: str
    is_anomaly: bool
    score: float
    severity: str
    model_version: str
    readings_analyzed: int
