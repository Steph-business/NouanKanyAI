"""Interfaces des capacités externes requises par les use cases."""

from app.application.ports.llm_service import LLMService
from app.application.ports.ml_service import AnomalyResult, ForecastResult, MLService
from app.application.ports.notification_service import NotificationService
from app.application.ports.report_service import GeneratedReport, ReportService

__all__ = [
    "AnomalyResult",
    "ForecastResult",
    "GeneratedReport",
    "LLMService",
    "MLService",
    "NotificationService",
    "ReportService",
]
