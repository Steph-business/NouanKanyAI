"""
app/ml/manager.py — Point d'entrée unique et façade centrale de la couche ML (ModelManager).
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.ml.anomaly_detector import AnomalyDetectionService
from app.ml.audit import AuditLogger
from app.ml.events import MLEventDispatcher, MLEventType
from app.ml.exceptions import ModelNotLoadedError
from app.ml.forecasting import ForecastingService
from app.ml.health import HealthChecker
from app.ml.loader import ModelLoader
from app.ml.metrics import ModelMetricsEvaluator
from app.ml.metrics_service import MetricsService
from app.ml.monitoring import MLInferenceMetrics
from app.ml.predictor import PredictionEngine
from app.ml.registry import RegistryManager
from app.ml.types import (
    AnomalyResult,
    HealthStatus,
    ModelInfo,
    PredictionResult,
)
from app.ml.validators import FeatureValidator

logger = logging.getLogger("nouankany.ml")


class ModelManager:
    """
    Point d'entrée unique et façade centrale pour l'ensemble des fonctionnalités ML.
    Masque l'intégralité de la complexité interne (chargement joblib, validation,
    registre, métriques, audit, événements) et offre une interface publique stricte et typée.
    """

    def __init__(self, artifacts_dir: Optional[str | Path] = None) -> None:
        """
        Initialise le gestionnaire de modèles avec ses composants sous-jacents.

        :param artifacts_dir: Chemin racine optionnel du dossier des artefacts.
        """
        self.loader = ModelLoader(artifacts_dir=artifacts_dir)
        self.registry = RegistryManager(registry_dir=self.loader.artifacts_dir / "registry")
        self.metrics_monitor = MLInferenceMetrics()
        self.audit_logger = AuditLogger(
            log_file_path=self.loader.artifacts_dir / "logs" / "ml_audit.jsonl"
        )
        self.event_dispatcher = MLEventDispatcher()
        self.health_checker = HealthChecker(
            loader=self.loader,
            registry=self.registry,
            metrics_monitor=self.metrics_monitor,
        )
        self.metrics_service = MetricsService(
            metrics_monitor=self.metrics_monitor,
            audit_logger=self.audit_logger,
            registry_manager=self.registry,
            health_checker=self.health_checker,
        )

        self._validator: Optional[FeatureValidator] = None
        self._forecasting_service: Optional[ForecastingService] = None
        self._anomaly_service: Optional[AnomalyDetectionService] = None
        self._prediction_engine: Optional[PredictionEngine] = None
        self._is_loaded: bool = False

        logger.debug("[ModelManager] Instance du gestionnaire initialisée avec observabilité.")

    def load_models(self) -> None:
        """
        Charge l'ensemble des modèles joblib, des métadonnées, des schémas et du registre.
        Prépare le moteur d'inférence pour la production.

        :raises ArtifactMissingError: Si un artefact est introuvable.
        :raises ManifestError: Si le manifeste est invalide.
        :raises ModelNotLoadedError: Si le chargement échoue.
        """
        # 1. Chargement du manifeste
        logger.info("Loading deployment manifest...")
        manifest = self.loader.load_manifest()
        version = manifest.get("version", "2.0.0")

        # 2. Résolution des chemins de modèles depuis le manifeste
        artifacts_cfg = manifest.get("artifacts", {})
        
        forecasting_rel_path = (
            artifacts_cfg.get("forecasting_model", {}).get("path")
            if isinstance(artifacts_cfg.get("forecasting_model"), dict)
            else "forecasting/xgb_pipeline_v2.0.0.joblib"
        )
        anomaly_rel_path = (
            artifacts_cfg.get("anomaly_model", {}).get("path")
            if isinstance(artifacts_cfg.get("anomaly_model"), dict)
            else "anomaly/if_pipeline_v2.0.0.joblib"
        )

        # Chargement des objets joblib
        xgb_model_obj = self.loader.load_joblib_model(forecasting_rel_path)
        logger.info("Loading XGBoost model... OK")

        if_model_obj = self.loader.load_joblib_model(anomaly_rel_path)
        logger.info("Loading Isolation Forest model... OK")

        # 3. Chargement des schémas de caractéristiques
        feature_schema = self.loader.load_feature_schema()
        self._validator = FeatureValidator(feature_schema)
        logger.info("Loading feature schemas... OK")

        # 4. Chargement des cartes de modèles et registre
        try:
            _ = self.registry.get_model_metadata("XGBoost_Forecaster")
            _ = self.registry.get_model_metadata("IsolationForest_AnomalyDetector")
        except Exception:
            pass
        logger.info("Loading model cards... OK")
        logger.info("Registry loaded successfully.")

        # 5. Récupération des caractéristiques réelles attendues par chaque modèle
        if hasattr(xgb_model_obj, "feature_names_in_"):
            forecasting_features = list(xgb_model_obj.feature_names_in_)
        elif "forecasting" in feature_schema and "features" in feature_schema["forecasting"]:
            forecasting_features = feature_schema["forecasting"]["features"]
        else:
            forecasting_features = [
                "power_kw", "power_kw_lag_1", "power_kw_lag_6", "power_kw_lag_24",
                "power_rolling_mean", "power_rolling_std", "hour", "day_of_week",
                "is_weekend", "is_peak_hour", "temperature_c"
            ]

        if hasattr(if_model_obj, "feature_names_in_"):
            anomaly_features = list(if_model_obj.feature_names_in_)
        elif "anomaly_detection" in feature_schema and "features" in feature_schema["anomaly_detection"]:
            anomaly_features = feature_schema["anomaly_detection"]["features"]
        else:
            anomaly_features = [
                "power_kw", "temperature_c", "vibration_hz", "pressure_bar",
                "power_rolling_std", "consumption_delta", "hour"
            ]

        # 6. Instanciation des services
        self._forecasting_service = ForecastingService(
            model=xgb_model_obj,
            model_name="XGBoost_Forecaster",
            version=version,
            feature_names=forecasting_features,
        )

        self._anomaly_service = AnomalyDetectionService(
            model=if_model_obj,
            model_name="IsolationForest_AnomalyDetector",
            version=version,
            feature_names=anomaly_features,
        )

        # 7. Moteur d'inférence avec observabilité
        self._prediction_engine = PredictionEngine(
            forecasting_service=self._forecasting_service,
            anomaly_service=self._anomaly_service,
            validator=self._validator,
            metrics_monitor=self.metrics_monitor,
            audit_logger=self.audit_logger,
            event_dispatcher=self.event_dispatcher,
        )

        self._is_loaded = True
        self.metrics_monitor.set_loaded_info(
            {
                "XGBoost_Forecaster": version,
                "IsolationForest_AnomalyDetector": version,
            }
        )

        # 8. Émission de l'événement de chargement réussi
        self.event_dispatcher.dispatch(
            event_type=MLEventType.MODEL_LOADED,
            model_name="ALL",
            model_version=version,
            payload={
                "models": ["XGBoost_Forecaster", "IsolationForest_AnomalyDetector"],
                "version": version,
            },
        )

        logger.info("ML subsystem ready.")

    def reload_models(self) -> None:
        """
        Recharge à chaud l'ensemble des modèles et schémas sans interrompre le service.
        """
        logger.info("[ModelManager] Demande de rechargement des modèles reçue...")
        self.load_models()
        self.event_dispatcher.dispatch(
            event_type=MLEventType.MODEL_RELOADED,
            payload={"action": "hot_reload", "status": "SUCCESS"},
        )
        logger.info("[ModelManager] Rechargement effectué avec succès.")

    def predict(
        self,
        input_data: Dict[str, Any],
        history: Optional[List[Dict[str, Any]]] = None,
        request_id: Optional[str] = None,
        strict_bounds: bool = False,
    ) -> PredictionResult:
        """
        Exécute la prévision de consommation énergétique à t+1.

        :param input_data: Dictionnaire des caractéristiques d'entrée.
        :param history: Historique chronologique optionnel pour calcul précis des retards.
        :param request_id: Identifiant unique optionnel de requête.
        :param strict_bounds: Si True, applique une vérification stricte des plages.
        :return: Instance typée `PredictionResult`.
        :raises ModelNotLoadedError: Si les modèles ne sont pas encore chargés.
        """
        if not self._is_loaded or self._prediction_engine is None:
            logger.error("[ModelManager] Tentative de prédiction avant chargement.")
            raise ModelNotLoadedError(
                "Les modèles ML n'ont pas été chargés. Appelez 'load_models()' au préalable."
            )
        return self._prediction_engine.predict_forecasting(
            raw_input=input_data,
            history=history,
            request_id=request_id,
            strict_bounds=strict_bounds,
        )

    def detect_anomaly(
        self,
        input_data: Dict[str, Any],
        previous_power: Optional[float] = None,
        request_id: Optional[str] = None,
        strict_bounds: bool = False,
    ) -> AnomalyResult:
        """
        Exécute l'analyse d'anomalie sur des données d'observation.

        :param input_data: Dictionnaire des caractéristiques transmises.
        :param previous_power: Puissance de l'itération précédente.
        :param request_id: Identifiant unique optionnel de requête.
        :param strict_bounds: Si True, applique une vérification stricte des plages.
        :return: Instance typée `AnomalyResult`.
        :raises ModelNotLoadedError: Si les modèles ne sont pas encore chargés.
        """
        if not self._is_loaded or self._prediction_engine is None:
            logger.error("[ModelManager] Tentative de détection avant chargement.")
            raise ModelNotLoadedError(
                "Les modèles ML n'ont pas été chargés. Appelez 'load_models()' au préalable."
            )
        return self._prediction_engine.predict_anomaly(
            raw_input=input_data,
            previous_power=previous_power,
            request_id=request_id,
            strict_bounds=strict_bounds,
        )

    def get_model_info(self, model_name: str) -> ModelInfo:
        """
        Récupère les informations descriptives et métriques d'un modèle spécifié.

        :param model_name: Nom du modèle recherché.
        :return: Instance typée `ModelInfo`.
        """
        return self.registry.get_model_info(model_name)

    def get_metrics(self) -> Dict[str, Any]:
        """
        Retourne la synthèse combinée des métriques d'entraînement et du moniteur d'inférence.

        :return: Dictionnaire complet des métriques du système.
        """
        return self.metrics_service.get_dashboard_summary(
            models_loaded=self._is_loaded,
            version=self.registry.get_latest_version() if self._is_loaded else "2.0.0",
        )

    def health_check(self) -> HealthStatus:
        """
        Diagnostique la santé opérationnelle de la couche ML.

        :return: Instance typée `HealthStatus`.
        """
        version = self.registry.get_latest_version() if self._is_loaded else "N/A"
        health = self.health_checker.check(
            models_loaded=self._is_loaded,
            registry_loaded=True,
            feature_schema_loaded=(self._validator is not None),
            version=version,
            forecasting_ready=(self._forecasting_service is not None and self._forecasting_service.model is not None),
            anomaly_ready=(self._anomaly_service is not None and self._anomaly_service.model is not None),
            additional_details=self.metrics_monitor.get_summary(),
        )

        self.event_dispatcher.dispatch(
            event_type=MLEventType.HEALTH_CHECKED,
            payload={"status": health.status, "version": health.version},
            level="WARNING" if health.status != "healthy" else "INFO",
        )

        return health

    def list_models(self) -> List[ModelInfo]:
        """
        Liste l'ensemble des modèles répertoriés dans la couche ML.

        :return: Liste d'instances `ModelInfo`.
        """
        known_models = ["XGBoost_Forecaster", "IsolationForest_AnomalyDetector"]
        result = []
        for name in known_models:
            try:
                result.append(self.get_model_info(name))
            except Exception as e:
                logger.warning(
                    f"[ModelManager] Impossible de lire les infos pour {name} : {e}"
                )
        return result
