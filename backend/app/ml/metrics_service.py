"""
app/ml/metrics_service.py — Service métier d'agrégation et d'exposition des métriques IA.

Fournit des statistiques opérationnelles, de performance, d'audit et de conformité
prêtes à être consommées par l'API REST et les tableaux de bord de surveillance.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional

from app.ml.audit import AuditLogger
from app.ml.health import HealthChecker
from app.ml.metrics import ModelMetricsEvaluator
from app.ml.monitoring import MLInferenceMetrics
from app.ml.registry import RegistryManager
from app.ml.types import HealthStatus

logger = logging.getLogger("nouankany.ml")


class MetricsService:
    """
    Service central de reporting et d'observabilité pour le sous-système ML.
    Consolide les métriques d'inférence temps réel, les métriques d'entraînement des modèles,
    l'historique d'audit et les bilans de santé.
    """

    def __init__(
        self,
        metrics_monitor: MLInferenceMetrics,
        audit_logger: AuditLogger,
        registry_manager: RegistryManager,
        health_checker: HealthChecker,
    ) -> None:
        """
        Initialise le service de métriques avec ses dépendances.

        :param metrics_monitor: Collecteur de métriques temps réel.
        :param audit_logger: Journal d'audit d'inférence.
        :param registry_manager: Gestionnaire du registre et model cards.
        :param health_checker: Contrôleur d'état de santé.
        """
        self.metrics_monitor = metrics_monitor
        self.audit_logger = audit_logger
        self.registry = registry_manager
        self.health_checker = health_checker

        logger.debug("[MetricsService] Service de métriques et observabilité initialisé.")

    def get_realtime_metrics(self) -> Dict[str, Any]:
        """
        Retourne les métriques opérationnelles en temps réel (débit, latences, erreurs).

        :return: Dictionnaire structuré des métriques runtime.
        """
        return self.metrics_monitor.get_summary()

    def get_latency_distribution(self) -> Dict[str, float]:
        """
        Retourne la distribution des latences (p50, p95, p99, moyenne).

        :return: Dictionnaire des percentiles.
        """
        percentiles = self.metrics_monitor.get_latency_percentiles()
        percentiles["avg_ms"] = round(self.metrics_monitor.avg_execution_time_ms, 2)
        return percentiles

    def get_model_training_metrics(self) -> Dict[str, Any]:
        """
        Extrait et synthétise les métriques d'évaluation d'entraînement des modèles enregistrés.

        :return: Dictionnaire combinant les métriques XGBoost et Isolation Forest.
        """
        xgb_metrics: Dict[str, Any] = {}
        if_metrics: Dict[str, Any] = {}

        try:
            xgb_info = self.registry.get_model_info("XGBoost_Forecaster")
            xgb_metrics = xgb_info.metrics
        except Exception as e:
            logger.debug(f"[MetricsService] Métriques XGBoost indisponibles : {e}")

        try:
            if_info = self.registry.get_model_info("IsolationForest_AnomalyDetector")
            if_metrics = if_info.metrics
        except Exception as e:
            logger.debug(f"[MetricsService] Métriques Isolation Forest indisponibles : {e}")

        return ModelMetricsEvaluator.format_summary(
            forecasting_metrics=xgb_metrics, anomaly_metrics=if_metrics
        )

    def get_audit_summary(self) -> Dict[str, Any]:
        """
        Retourne la synthèse agrégée de l'audit des inférences.

        :return: Dictionnaire des statistiques d'audit.
        """
        return self.audit_logger.get_summary()

    def get_recent_audit_records(
        self,
        limit: int = 50,
        model_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Récupère les enregistrements d'audit récents sérialisés.

        :param limit: Nombre maximum d'enregistrements.
        :param model_name: Filtre optionnel sur le modèle.
        :param status: Filtre optionnel sur le statut (SUCCESS, ERROR).
        :return: Liste de dictionnaires d'audit.
        """
        records = self.audit_logger.get_records(
            limit=limit, model_name=model_name, status=status
        )
        return [r.model_dump(mode="json") for r in records]

    def get_system_health(
        self,
        models_loaded: bool = True,
        registry_loaded: bool = True,
        feature_schema_loaded: bool = True,
        version: str = "2.0.0",
    ) -> HealthStatus:
        """
        Exécute et retourne le diagnostic de santé complet du sous-système ML.

        :return: Instance typée `HealthStatus`.
        """
        return self.health_checker.check(
            models_loaded=models_loaded,
            registry_loaded=registry_loaded,
            feature_schema_loaded=feature_schema_loaded,
            version=version,
        )

    def get_dashboard_summary(
        self,
        models_loaded: bool = True,
        version: str = "2.0.0",
    ) -> Dict[str, Any]:
        """
        Génère un tableau de bord complet unifié pour l'observabilité IA de NouanKanyAI.

        :param models_loaded: Statut de chargement des modèles.
        :param version: Version active.
        :return: Dictionnaire complet combinant santé, runtime, qualité et audit.
        """
        health = self.get_system_health(
            models_loaded=models_loaded,
            registry_loaded=True,
            feature_schema_loaded=True,
            version=version,
        )

        rt_metrics = self.get_realtime_metrics()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "health": health.model_dump(mode="json"),
            "runtime_metrics": rt_metrics,
            "runtime_inference": rt_metrics,
            "training_metrics": self.get_model_training_metrics(),
            "audit_summary": self.get_audit_summary(),
        }
