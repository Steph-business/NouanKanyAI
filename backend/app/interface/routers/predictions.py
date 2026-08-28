"""
app/interface/routers/predictions.py — Routeur FastAPI pour les prévisions de charge d'interface.

Expose un endpoint simplifié de calcul de projection de charge énergétique.
"""

from typing import Any, Dict
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class PredictionPayload(BaseModel):
    """
    Paramètres d'entrée pour la prévision de charge simplifiée.
    """
    machine_id: str = Field(..., description="Identifiant unique de la machine")
    temperature_c: float = Field(..., description="Température mesurée en degrés Celsius")
    vibration_hz: float = Field(..., description="Fréquence de vibration mesurée en Hertz")
    pressure_bar: float = Field(..., description="Pression enregistrée en bars")
    hours_ahead: int = Field(default=24, description="Horizon temporel de prévision en heures")


@router.post(
    "/predictions",
    summary="Calcul de prévision de charge simplifiée",
    description="Estime la puissance appelée (kW) selon les variables environnementales et mécaniques.",
)
def get_predictions(payload: PredictionPayload) -> Dict[str, Any]:
    """
    Calcule une estimation de charge basée sur les paramètres de l'équipement.
    """
    # Approximation pondérée de la charge prévisionnelle
    predicted_load = round(
        payload.temperature_c * 0.8 + payload.vibration_hz * 0.3 + payload.pressure_bar * 0.2, 2
    )
    return {
        "machine_id": payload.machine_id,
        "predicted_load_kw": predicted_load,
        "hours_ahead": payload.hours_ahead,
        "status": "ok",
    }
