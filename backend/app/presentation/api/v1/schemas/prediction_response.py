"""Schémas HTTP de sortie pour les prévisions et diagnostics ML."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PredictionResponse(BaseModel):
    """Réponse HTTP sérialisable de prévision applicative."""

    model_config = ConfigDict(frozen=True)

    machine_id: str
    predictions: list[float]
    confidence_interval: tuple[float, float]
    model_version: str
    timestamp: datetime
