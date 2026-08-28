"""
app/ml/predictor.py — Moteur central d'orchestration d'inférence (PredictionEngine).

Valide les caractéristiques d'entrée via `FeatureValidator`, génère un identifiant unique (UUID),
exécute l'inférence via les services spécialisés (`ForecastingService` et `AnomalyDetectionService`),
mesure le temps d'exécution, trace les transactions via `AuditLogger`, émet des événements
internes via `MLEventDispatcher`, et enregistre les métriques runtime.
"""

from datetime import datetime, timezone
import logging
import time
from typing import Any, Dict, List, Optional, Union
import uuid
import pandas as pd

from app.ml.anomaly_detector import AnomalyDetectionService
from app.ml.audit import AuditLogger
from app.ml.events import MLEventDispatcher, MLEventType
from app.ml.exceptions import FeatureValidationError, PredictionError
from app.ml.forecasting import ForecastingService
from app.ml.monitoring import MLInferenceMetrics
from app.ml.preprocessing import compute_data_hash
from app.ml.types import AnomalyResult, PredictionResult
from app.ml.validators import FeatureValidator

logger = logging.getLogger("nouankany.ml")


class PredictionEngine:
    """
    Point d'orchestration central pour toutes les opérations de prédiction et de détection.
    Garantit la validation des entrées, la génération d'un UUID par requête,
    l'enregistrement des métriques de latence, la journalisation d'audit et l'émission d'événements.
    """

    def __init__(
        self,
        forecasting_service: ForecastingService,
        anomaly_service: AnomalyDetectionService,
        validator: FeatureValidator,
        metrics_monitor: MLInferenceMetrics,
        audit_logger: Optional[AuditLogger] = None,
        event_dispatcher: Optional[MLEventDispatcher] = None,
    ) -> None:
        """
        Initialise le moteur de prédiction avec ses composants injectés.

        :param forecasting_service: Service dédié au modèle XGBoost.
        :param anomaly_service: Service dédié au modèle Isolation Forest.
        :param validator: Composant de validation des caractéristiques d'entrée.
        :param metrics_monitor: Moniteur de suivi des métriques en temps réel.
        :param audit_logger: Composant de traçabilité et d'audit d'inférence.
        :param event_dispatcher: Bus d'événements ML interne.
        """
        self.forecasting_service = forecasting_service
        self.anomaly_service = anomaly_service
        self.validator = validator
        self.metrics_monitor = metrics_monitor
        self.audit_logger = audit_logger or AuditLogger()
        self.event_dispatcher = event_dispatcher or MLEventDispatcher()

        logger.debug("[PredictionEngine] Moteur d'inférence initialisé avec observabilité complète.")

    def predict_forecasting(
        self,
        raw_input: Union[Dict[str, Any], pd.DataFrame],
        history: Optional[List[Dict[str, Any]]] = None,
        request_id: Optional[str] = None,
        strict_bounds: bool = False,
    ) -> PredictionResult:
        """
        Orchestre une prédiction de prévision énergétique avec validation, audit et observabilité.

        :param raw_input: Dictionnaire brut ou DataFrame des caractéristiques.
        :param history: Historique chronologique optionnel pour calcul précis des retards.
        :param request_id: Identifiant optionnel (un UUID est généré par défaut).
        :param strict_bounds: Si True, rejette les valeurs hors limites du schéma.
        :return: Instance typée `PredictionResult`.
        :raises FeatureValidationError: Si les entrées sont invalides.
        :raises PredictionError: En cas d'échec d'inférence.
        """
        req_id = request_id or str(uuid.uuid4())
        start_time = time.perf_counter()
        input_hash = compute_data_hash(raw_input)

        self.event_dispatcher.dispatch(
            event_type=MLEventType.PREDICTION_REQUESTED,
            request_id=req_id,
            model_name=self.forecasting_service.model_name,
            model_version=self.forecasting_service.version,
            payload={"operation": "forecasting", "input_hash": input_hash},
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
                execution_time_ms=result.metadata.execution_time_ms,
                is_anomaly=False,
                model_name=self.forecasting_service.model_name,
            )

            # 4. Enregistrement d'audit
            self.audit_logger.log_inference(
                request_id=req_id,
                operation="forecasting",
                model_name=self.forecasting_service.model_name,
                model_version=self.forecasting_service.version,
                execution_time_ms=result.metadata.execution_time_ms,
                input_summary={"power_kw": validated.get("power_kw")},
                output_summary={"predicted_value": result.predicted_value, "unit": result.unit},
                input_hash=input_hash,
                status="SUCCESS",
            )

            # 5. Émission d'événement de succès
            self.event_dispatcher.dispatch(
                event_type=MLEventType.PREDICTION_SUCCESS,
                request_id=req_id,
                model_name=self.forecasting_service.model_name,
                model_version=self.forecasting_service.version,
                payload={
                    "predicted_value": result.predicted_value,
                    "execution_time_ms": result.metadata.execution_time_ms,
                },
            )

            return result

        except FeatureValidationError as fve:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            self.metrics_monitor.record_error(
                error_message=str(fve),
                is_validation=True,
                model_name=self.forecasting_service.model_name,
            )
            self.audit_logger.log_inference(
                request_id=req_id,
                operation="forecasting",
                model_name=self.forecasting_service.model_name,
                model_version=self.forecasting_service.version,
                execution_time_ms=elapsed_ms,
                input_summary={"raw_input_type": str(type(raw_input))},
                output_summary={},
                input_hash=input_hash,
                status="VALIDATION_FAILED",
                error_message=str(fve),
            )
            self.event_dispatcher.dispatch(
                event_type=MLEventType.VALIDATION_ERROR,
                request_id=req_id,
                model_name=self.forecasting_service.model_name,
                model_version=self.forecasting_service.version,
                payload={"error": str(fve), "details": fve.details},
                level="WARNING",
            )
            raise

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            self.metrics_monitor.record_error(
                error_message=str(e),
                is_validation=False,
                model_name=self.forecasting_service.model_name,
            )
            self.audit_logger.log_inference(
                request_id=req_id,
                operation="forecasting",
                model_name=self.forecasting_service.model_name,
                model_version=self.forecasting_service.version,
                execution_time_ms=elapsed_ms,
                input_summary={},
                output_summary={},
                input_hash=input_hash,
                status="ERROR",
                error_message=str(e),
            )
            self.event_dispatcher.dispatch(
                event_type=MLEventType.PREDICTION_ERROR,
                request_id=req_id,
                model_name=self.forecasting_service.model_name,
                model_version=self.forecasting_service.version,
                payload={"error": str(e)},
                level="ERROR",
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
        Orchestre une détection d'anomalie sur des données d'observation capteurs avec audit et événements.

        :param raw_input: Dictionnaire brut ou DataFrame d'observation.
        :param previous_power: Puissance de l'itération précédente (optionnel).
        :param request_id: Identifiant optionnel (un UUID est généré par défaut).
        :param strict_bounds: Si True, applique une vérification stricte des plages.
        :return: Instance typée `AnomalyResult`.
        :raises FeatureValidationError: Si les entrées sont invalides.
        :raises PredictionError: En cas d'échec du modèle.
        """
        req_id = request_id or str(uuid.uuid4())
        start_time = time.perf_counter()
        input_hash = compute_data_hash(raw_input)

        self.event_dispatcher.dispatch(
            event_type=MLEventType.PREDICTION_REQUESTED,
            request_id=req_id,
            model_name=self.anomaly_service.model_name,
            model_version=self.anomaly_service.version,
            payload={"operation": "anomaly_detection", "input_hash": input_hash},
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
                model_name=self.anomaly_service.model_name,
            )

            # 4. Enregistrement d'audit
            self.audit_logger.log_inference(
                request_id=req_id,
                operation="anomaly_detection",
                model_name=self.anomaly_service.model_name,
                model_version=self.anomaly_service.version,
                execution_time_ms=result.metadata.execution_time_ms,
                input_summary={
                    "power_kw": validated.get("power_kw"),
                    "temperature_c": validated.get("temperature_c"),
                },
                output_summary={
                    "is_anomaly": result.is_anomaly,
                    "score": result.score,
                    "severity": result.severity,
                },
                input_hash=input_hash,
                status="SUCCESS",
            )

            # 5. Émission d'événement spécifique
            event_type = (
                MLEventType.ANOMALY_DETECTED
                if result.is_anomaly
                else MLEventType.ANOMALY_CHECK_NORMAL
            )
            self.event_dispatcher.dispatch(
                event_type=event_type,
                request_id=req_id,
                model_name=self.anomaly_service.model_name,
                model_version=self.anomaly_service.version,
                payload={
                    "is_anomaly": result.is_anomaly,
                    "severity": result.severity,
                    "score": result.score,
                    "probability": result.probability,
                    "execution_time_ms": result.metadata.execution_time_ms,
                },
                level="WARNING" if result.is_anomaly else "INFO",
            )

            return result

        except FeatureValidationError as fve:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            self.metrics_monitor.record_error(
                error_message=str(fve),
                is_validation=True,
                model_name=self.anomaly_service.model_name,
            )
            self.audit_logger.log_inference(
                request_id=req_id,
                operation="anomaly_detection",
                model_name=self.anomaly_service.model_name,
                model_version=self.anomaly_service.version,
                execution_time_ms=elapsed_ms,
                input_summary={"raw_input_type": str(type(raw_input))},
                output_summary={},
                input_hash=input_hash,
                status="VALIDATION_FAILED",
                error_message=str(fve),
            )
            self.event_dispatcher.dispatch(
                event_type=MLEventType.VALIDATION_ERROR,
                request_id=req_id,
                model_name=self.anomaly_service.model_name,
                model_version=self.anomaly_service.version,
                payload={"error": str(fve), "details": fve.details},
                level="WARNING",
            )
            raise

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            self.metrics_monitor.record_error(
                error_message=str(e),
                is_validation=False,
                model_name=self.anomaly_service.model_name,
            )
            self.audit_logger.log_inference(
                request_id=req_id,
                operation="anomaly_detection",
                model_name=self.anomaly_service.model_name,
                model_version=self.anomaly_service.version,
                execution_time_ms=elapsed_ms,
                input_summary={},
                output_summary={},
                input_hash=input_hash,
                status="ERROR",
                error_message=str(e),
            )
            self.event_dispatcher.dispatch(
                event_type=MLEventType.PREDICTION_ERROR,
                request_id=req_id,
                model_name=self.anomaly_service.model_name,
                model_version=self.anomaly_service.version,
                payload={"error": str(e)},
                level="ERROR",
            )
            if isinstance(e, PredictionError):
                raise
            raise PredictionError(
                f"Erreur d'exécution de détection d'anomalie : {e}",
                details={"request_id": req_id, "error": str(e)},
            ) from e
