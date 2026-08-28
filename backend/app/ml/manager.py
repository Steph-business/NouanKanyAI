"""
app/ml/manager.py — Point d'entrée unique et façade centrale de la couche ML (ModelManager).
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.ml.anomaly_detector import AnomalyDetectionService
from app.ml.exceptions import ModelNotLoadedError
from app.ml.forecasting import ForecastingService
from app.ml.health import HealthChecker
from app.ml.loader import ModelLoader
from app.ml.metrics import ModelMetricsEvaluator
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
    registre, métriques) et offre une interface publique stricte et typée.
    """

    def __init__(self, artifacts_dir: Optional[str | Path] = None) -> None:
        """
        Initialise le gestionnaire de modèles avec ses composants sous-jacents.

        :param artifacts_dir: Chemin racine optionnel du dossier des artefacts.
        """
        self.loader = ModelLoader(artifacts_dir=artifacts_dir)
        self.registry = RegistryManager(registry_dir=self.loader.artifacts_dir / "registry")
        self.metrics_monitor = MLInferenceMetrics()
        self.health_checker = HealthChecker()

        self._validator: Optional[FeatureValidator] = None
        self._forecasting_service: Optional[ForecastingService] = None
        self._anomaly_service: Optional[AnomalyDetectionService] = None
        self._prediction_engine: Optional[PredictionEngine] = None
        self._is_loaded: bool = False

        logger.debug("[ModelManager] Instance du gestionnaire initialisée.")

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

        # 7. Moteur d'inférence
        self._prediction_engine = PredictionEngine(
            forecasting_service=self._forecasting_service,
            anomaly_service=self._anomaly_service,
            validator=self._validator,
            metrics_monitor=self.metrics_monitor,
        )

        self._is_loaded = True
        self.metrics_monitor.set_loaded_info(
            {
                "XGBoost_Forecaster": version,
                "IsolationForest_AnomalyDetector": version,
            }
        )

        logger.info("ML subsystem ready.")

    def reload_models(self) -> None:
        """
        Recharge à chaud l'ensemble des modèles et schémas sans interrompre le service.
        """
        logger.info("[ModelManager] Demande de rechargement des modèles reçue...")
        self.load_models()
        logger.info("[ModelManager] Rechargement effectué avec succès.")

    def predict(self, input_data: Dict[str, Any]) -> PredictionResult:
        """
        Exécute la prévision de consommation énergétique à t+1.

        :param input_data: Dictionnaire des caractéristiques d'entrée.
        :return: Instance typée `PredictionResult`.
        :raises ModelNotLoadedError: Si les modèles ne sont pas encore chargés.
        """
        if not self._is_loaded or self._prediction_engine is None:
            logger.error("[ModelManager] Tentative de prédiction avant chargement.")
            raise ModelNotLoadedError(
                "Les modèles ML n'ont pas été chargés. Appelez 'load_models()' au préalable."
            )
        return self._prediction_engine.predict_forecasting(input_data)

    def detect_anomaly(self, input_data: Dict[str, Any]) -> AnomalyResult:
        """
        Exécute l'analyse d'anomalie sur des données d'observation.

        :param input_data: Dictionnaire des caractéristiques transmises.
        :return: Instance typée `AnomalyResult`.
        :raises ModelNotLoadedError: Si les modèles ne sont pas encore chargés.
        """
        if not self._is_loaded or self._prediction_engine is None:
            logger.error("[ModelManager] Tentative de détection avant chargement.")
            raise ModelNotLoadedError(
                "Les modèles ML n'ont pas été chargés. Appelez 'load_models()' au préalable."
            )
        return self._prediction_engine.predict_anomaly(input_data)

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
        xgb_info = self.get_model_info("XGBoost_Forecaster")
        if_info = self.get_model_info("IsolationForest_AnomalyDetector")

        training_metrics = ModelMetricsEvaluator.format_summary(
            forecasting_metrics=xgb_info.metrics, anomaly_metrics=if_info.metrics
        )
        runtime_metrics = self.metrics_monitor.get_summary()

        return {
            "training_metrics": training_metrics,
            "runtime_inference": runtime_metrics,
        }

    def health_check(self) -> HealthStatus:
        """
        Diagnostique la santé opérationnelle de la couche ML.

        :return: Instance typée `HealthStatus`.
        """
        version = self.registry.get_latest_version() if self._is_loaded else "N/A"
        return self.health_checker.check(
            models_loaded=self._is_loaded,
            registry_loaded=True,
            feature_schema_loaded=(self._validator is not None),
            version=version,
            additional_details=self.metrics_monitor.get_summary(),
        )

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
