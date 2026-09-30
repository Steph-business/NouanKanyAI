"""Schémas HTTP d'entrée pour les demandes de prévision."""

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Contrat HTTP minimal de prévision utilisé par l'API versionnée."""

    machine_id: str = Field(..., min_length=1)
    horizon_hours: int = Field(default=24, ge=1, le=168)
