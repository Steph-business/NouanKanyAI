"""
app/ml/predictor.py — Moteur d'orchestration des prédictions et de détection d'anomalies.
"""

import logging
from typing import Any, Dict, Optional

from app.ml.anomaly_detector import AnomalyDetectionService
from app.ml.exceptions import FeatureValidationError, PredictionError
from app.ml.forecasting import ForecastingService
from app.ml.monitoring import MLInferenceMetrics
from app.ml.types import AnomalyResult, PredictionResult
from app.ml.validators import FeatureValidator

logger = logging.getLogger("nouankany.ml")


class PredictionEngine:
    """
    Moteur central de prédiction et d'inférence.
    Reçoit les requêtes brutes, orchestre la validation des caractéristiques
    via `FeatureValidator`, délègue l'exécution aux services spécialisés
    (`ForecastingService` / `AnomalyDetectionService`) et met à jour les métriques d'inférence.
    """

    def __init__(
        self,
        forecasting_service: ForecastingService,
        anomaly_service: AnomalyDetectionService,
        validator: FeatureValidator,
        metrics_monitor: MLInferenceMetrics,
    ) -> None:
        """
        Initialise le moteur de prédiction avec injection de ses dépendances.

        :param forecasting_service: Service dédié au modèle XGBoost.
        :param anomaly_service: Service dédié au modèle Isolation Forest.
        :param validator: Composant de validation des caractéristiques d'entrée.
        :param metrics_monitor: Moniteur de suivi des métriques en temps réel.
        """
        self.forecasting_service = forecasting_service
        self.anomaly_service = anomaly_service
        self.validator = validator
        self.metrics_monitor = metrics_monitor
        logger.debug("[PredictionEngine] Moteur d'inférence initialisé avec succès.")

    def predict_forecasting(self, raw_input: Dict[str, Any]) -> PredictionResult:
        """
        Orchestre une prédiction de prévision énergétique.

        :param raw_input: Dictionnaire brut des caractéristiques transmises.
        :return: Instance typée `PredictionResult`.
        """
        try:
            validated = self.validator.validate(
                raw_input, required_features=self.forecasting_service.feature_names
            )
            result = self.forecasting_service.predict(validated)
            self.metrics_monitor.record_inference(
                execution_time_ms=result.metadata.execution_time_ms, is_anomaly=False
            )
            return result
        except Exception as e:
            self.metrics_monitor.record_error()
            logger.error(f"[PredictionEngine] Erreur prévision : {e}")
            if isinstance(e, (PredictionError, FeatureValidationError)):
                raise
            raise PredictionError(f"Erreur d'exécution de prévision : {e}") from e

    def predict_anomaly(self, raw_input: Dict[str, Any]) -> AnomalyResult:
        """
        Orchestre une détection d'anomalie sur des données d'observation.

        :param raw_input: Dictionnaire brut des caractéristiques d'entrée.
        :return: Instance typée `AnomalyResult`.
        """
        try:
            validated = self.validator.validate(
                raw_input, required_features=self.anomaly_service.feature_names
            )
            result = self.anomaly_service.detect(validated)
            self.metrics_monitor.record_inference(
                execution_time_ms=result.metadata.execution_time_ms,
                is_anomaly=result.is_anomaly,
            )
            return result
        except Exception as e:
            self.metrics_monitor.record_error()
            logger.error(f"[PredictionEngine] Erreur détection anomalie : {e}")
            if isinstance(e, (PredictionError, FeatureValidationError)):
                raise
            raise PredictionError(
                f"Erreur d'exécution de détection d'anomalie : {e}"
            ) from e
