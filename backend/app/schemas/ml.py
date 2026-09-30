"""Compatibilité d'import vers les schémas HTTP ML de Presentation."""

from app.presentation.api.v1.schemas.ml import (
    AnomalyDetectionRequest,
    AnomalyResponseSchema,
    ErrorDetail,
    ForecastingRequest,
    PredictionMetadataSchema,
    PredictionResponseSchema,
    ReloadResponseSchema,
    StandardErrorResponse,
)

__all__ = [
    "AnomalyDetectionRequest", "AnomalyResponseSchema", "ErrorDetail", "ForecastingRequest",
    "PredictionMetadataSchema", "PredictionResponseSchema", "ReloadResponseSchema",
    "StandardErrorResponse",
]
