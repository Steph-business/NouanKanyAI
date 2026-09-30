"""Compatibilité d'import vers le routeur de prévisions de Presentation."""

from app.presentation.api.v1.routes.predictions import PredictionPayload, get_predictions, router

__all__ = ["PredictionPayload", "get_predictions", "router"]
