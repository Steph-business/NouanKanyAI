"""Objets de transfert applicatifs indépendants des schémas HTTP."""

from app.application.dto.anomaly_dto import DetectAnomalyCommand, DetectAnomalyResult
from app.application.dto.prediction_dto import PredictConsumptionCommand, PredictConsumptionResult

__all__ = [
    "DetectAnomalyCommand",
    "DetectAnomalyResult",
    "PredictConsumptionCommand",
    "PredictConsumptionResult",
]
