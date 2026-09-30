"""Commandes et résultats du use case de prévision énergétique."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PredictConsumptionCommand:
    """Demande applicative de prévision pour une machine."""

    machine_id: str
    horizon_hours: int = 24


@dataclass(frozen=True)
class PredictConsumptionResult:
    """Résultat métier normalisé de prévision."""

    machine_id: str
    predictions: list[float]
    confidence_interval: tuple[float, float]
    model_version: str
