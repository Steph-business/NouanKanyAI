"""
app/ml/ — Module principal de la couche Machine Learning de NouanKanyAI.

Expose le gestionnaire central `ModelManager` ainsi que les services,
valideurs, registres et exceptions du domaine ML.
"""

import logging

# Configuration du logger dédié au sous-système ML
logger = logging.getLogger("nouankany.ml")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _formatter = logging.Formatter(
        "%(levelname)-5s %(message)s"
    )
    _handler.setFormatter(_formatter)
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)

from app.ml.anomaly_detector import AnomalyDetectionService
from app.ml.exceptions import (
    ArtifactMissingError,
    FeatureValidationError,
    ManifestError,
    MLException,
    ModelNotLoadedError,
    PredictionError,
    RegistryError,
)
from app.ml.forecasting import ForecastingService
from app.ml.health import HealthChecker
from app.ml.loader import ModelLoader
from app.ml.manager import ModelManager
from app.ml.metrics import ModelMetricsEvaluator, PerformanceMetrics
from app.ml.monitoring import MLInferenceMetrics
from app.ml.predictor import PredictionEngine
from app.ml.registry import RegistryManager
from app.ml.types import (
    AnomalyResult,
    HealthStatus,
    ModelInfo,
    PredictionMetadata,
    PredictionResult,
    RegistryEntry,
)
from app.ml.validators import FeatureValidator

__all__ = [
    "ModelManager",
    "ModelLoader",
    "RegistryManager",
    "PredictionEngine",
    "ForecastingService",
    "AnomalyDetectionService",
    "FeatureValidator",
    "MLInferenceMetrics",
    "ModelMetricsEvaluator",
    "HealthChecker",
    "PerformanceMetrics",
    "PredictionResult",
    "AnomalyResult",
    "ModelInfo",
    "RegistryEntry",
    "HealthStatus",
    "PredictionMetadata",
    "MLException",
    "ModelNotLoadedError",
    "RegistryError",
    "FeatureValidationError",
    "PredictionError",
    "ManifestError",
    "ArtifactMissingError",
]
