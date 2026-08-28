"""
app/ml/predictor.py — Moteur central d'orchestration d'inférence (PredictionEngine).

Valide les caractéristiques d'entrée via `FeatureValidator`, génère un identifiant unique (UUID),
exécute l'inférence via les services spécialisés (`ForecastingService` et `AnomalyDetectionService`),
mesure le temps d'exécution, journalise chaque opération et enregistre les métriques runtime.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from app.ml.anomaly_detector import AnomalyDetectionService
from app.ml.exceptions import FeatureValidationError, PredictionError
from app.ml.forecasting import ForecastingService
from app.ml.monitoring import MLInferenceMetrics
from app.ml.types import AnomalyResult, PredictionResult
from app.ml.validators import FeatureValidator

logger = logging.getLogger("nouankany.ml")


class PredictionEngine:
    """
    Point d'orchestration central pour toutes les opérations de prédiction et de détection.
    Garantit la validation des entrées, la génération d'un UUID par requête,
    l'enregistrement des métriques de latence et la journalisation unifiée.
    """

    def __init__(
        self,
        forecasting_service: ForecastingService,
        anomaly_service: AnomalyDetectionService,
        validator: FeatureValidator,
        metrics_monitor: MLInferenceMetrics,
    ) -> None:
        """
        Initialise le moteur de prédiction avec ses composants injectés.

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

    def predict_forecasting(
        self,
        raw_input: Union[Dict[str, Any], pd.DataFrame],
        history: Optional[List[Dict[str, Any]]] = None,
        request_id: Optional[str] = None,
        strict_bounds: bool = False,
    ) -> PredictionResult:
        """
        Orchestre une prédiction de prévision énergétique avec validation et traçabilité.

        :param raw_input: Dictionnaire brut ou DataFrame des caractéristiques.
        :param history: Historique chronologique optionnel pour calcul précis des retards.
        :param request_id: Identifiant optionnel (un UUID est généré par défaut).
        :param strict_bounds: Si True, rejette les valeurs hors limites du schéma.
        :return: Instance typée `PredictionResult`.
        :raises FeatureValidationError: Si les entrées sont invalides.
        :raises PredictionError: En cas d'échec d'inférence.
        """
        req_id = request_id or str(uuid.uuid4())
        logger.info(
            f"[PredictionEngine] [req_id={req_id}] Réception d'une demande de prévision énergétique."
        )

        try:
            # 1. Validation des caractéristiques
            validated = self.validator.validate_forecasting(
                raw_input, strict_bounds=strict_bounds
            )

            # 2. Exécution du service de prévision
            result = self.forecasting_service.predict(
                features=validated, history=history, request_id=req_id
            )

            # 3. Enregistrement des métriques de runtime
            self.metrics_monitor.record_inference(
                execution_time_ms=result.metadata.execution_time_ms, is_anomaly=False
            )

            logger.info(
                f"[PredictionEngine] [req_id={req_id}] Prévision terminée avec succès: "
                f"{result.predicted_value} {result.unit} (latence: {result.metadata.execution_time_ms}ms)"
            )
            return result

        except FeatureValidationError as fve:
            self.metrics_monitor.record_error()
            logger.warning(
                f"[PredictionEngine] [req_id={req_id}] Erreur de validation des entrées : {fve}"
            )
            raise
        except Exception as e:
            self.metrics_monitor.record_error()
            logger.error(
                f"[PredictionEngine] [req_id={req_id}] Erreur critique lors de la prévision : {e}"
            )
            if isinstance(e, PredictionError):
                raise
            raise PredictionError(
                f"Erreur d'exécution de prévision : {e}",
                details={"request_id": req_id, "error": str(e)},
            ) from e

    def predict_anomaly(
        self,
        raw_input: Union[Dict[str, Any], pd.DataFrame],
        previous_power: Optional[float] = None,
        request_id: Optional[str] = None,
        strict_bounds: bool = False,
    ) -> AnomalyResult:
        """
        Orchestre une détection d'anomalie sur des données d'observation capteurs.

        :param raw_input: Dictionnaire brut ou DataFrame d'observation.
        :param previous_power: Puissance de l'itération précédente (optionnel).
        :param request_id: Identifiant optionnel (un UUID est généré par défaut).
        :param strict_bounds: Si True, applique une vérification stricte des plages.
        :return: Instance typée `AnomalyResult`.
        :raises FeatureValidationError: Si les entrées sont invalides.
        :raises PredictionError: En cas d'échec du modèle.
        """
        req_id = request_id or str(uuid.uuid4())
        logger.info(
            f"[PredictionEngine] [req_id={req_id}] Réception d'une demande de détection d'anomalie."
        )

        try:
            # 1. Validation des caractéristiques d'anomalie
            validated = self.validator.validate_anomaly(
                raw_input, strict_bounds=strict_bounds
            )

            # 2. Exécution du service de détection
            result = self.anomaly_service.detect(
                features=validated,
                previous_power=previous_power,
                request_id=req_id,
            )

            # 3. Enregistrement des métriques runtime
            self.metrics_monitor.record_inference(
                execution_time_ms=result.metadata.execution_time_ms,
                is_anomaly=result.is_anomaly,
            )

            logger.info(
                f"[PredictionEngine] [req_id={req_id}] Détection terminée: "
                f"anomalie={result.is_anomaly}, sévérité={result.severity}, score={result.score} "
                f"(latence: {result.metadata.execution_time_ms}ms)"
            )
            return result

        except FeatureValidationError as fve:
            self.metrics_monitor.record_error()
            logger.warning(
                f"[PredictionEngine] [req_id={req_id}] Erreur de validation d'anomalie : {fve}"
            )
            raise
        except Exception as e:
            self.metrics_monitor.record_error()
            logger.error(
                f"[PredictionEngine] [req_id={req_id}] Erreur critique lors de la détection : {e}"
            )
            if isinstance(e, PredictionError):
                raise
            raise PredictionError(
                f"Erreur d'exécution de détection d'anomalie : {e}",
                details={"request_id": req_id, "error": str(e)},
            ) from e
