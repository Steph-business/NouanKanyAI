"""Actions métier exécutables et coordonnées par la couche application."""

from app.application.use_cases.calculate_invoice import CalculateInvoiceUseCase
from app.application.use_cases.detect_anomaly import DetectAnomalyUseCase
from app.application.use_cases.generate_report import GenerateReportUseCase
from app.application.use_cases.predict_consumption import PredictConsumptionUseCase

__all__ = [
    "CalculateInvoiceUseCase",
    "DetectAnomalyUseCase",
    "GenerateReportUseCase",
    "PredictConsumptionUseCase",
]
