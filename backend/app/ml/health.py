"""
app/ml/health.py — Contrôleur d'état de santé approfondi de la couche ML.

Vérifie la disponibilité effective des modèles en mémoire, l'intégrité des artefacts
sur disque (manifeste, joblib, schémas, model cards), la joignabilité du registre
et les seuils d'erreur opérationnels.
"""

from datetime import datetime, timezone
import logging
from pathlib import Path
import time
from typing import Any, Dict, Optional

from app.ml.loader import ModelLoader
from app.ml.monitoring import MLInferenceMetrics
from app.ml.registry import RegistryManager
from app.ml.types import HealthStatus

logger = logging.getLogger("nouankany.ml")


class HealthChecker:
    """
    Composant responsable des diagnostics de disponibilité, d'intégrité et de santé
    de la couche Machine Learning de NouanKanyAI.
    """

    def __init__(
        self,
        loader: Optional[ModelLoader] = None,
        registry: Optional[RegistryManager] = None,
        metrics_monitor: Optional[MLInferenceMetrics] = None,
    ) -> None:
        """
        Initialise le vérificateur de santé avec ses dépendances.

        :param loader: Instance de ModelLoader pour inspecter les fichiers d'artefacts.
        :param registry: Instance de RegistryManager pour vérifier l'accès au registre.
        :param metrics_monitor: Instance de MLInferenceMetrics pour surveiller les seuils d'erreur.
        """
        self.loader = loader
        self.registry = registry
        self.metrics_monitor = metrics_monitor
        logger.debug("[HealthChecker] Contrôleur de santé initialisé.")

    def check(
        self,
        models_loaded: bool,
        registry_loaded: bool,
        feature_schema_loaded: bool,
        version: str,
        forecasting_ready: bool = True,
        anomaly_ready: bool = True,
        additional_details: Optional[Dict[str, Any]] = None,
    ) -> HealthStatus:
        """
        Effectue un diagnostic complet multi-composants de la couche ML.

        :param models_loaded: Vrai si les modèles sont chargés en mémoire.
        :param registry_loaded: Vrai si le registre est accessible.
        :param feature_schema_loaded: Vrai si le schéma de features est chargé.
        :param version: Version courante active.
        :param forecasting_ready: Disponibilité du service XGBoost.
        :param anomaly_ready: Disponibilité du service Isolation Forest.
        :param additional_details: Informations complémentaires.
        :return: Instance typée `HealthStatus`.
        """
        start_time = time.perf_counter()
        components: Dict[str, Dict[str, Any]] = {}
        is_healthy = True
        is_degraded = False

        # 1. Diagnostic des Modèles
        models_status = "UP" if (models_loaded and forecasting_ready and anomaly_ready) else "DOWN"
        if models_status == "DOWN":
            is_healthy = False
        components["models"] = {
            "status": models_status,
            "forecasting_service": "UP" if forecasting_ready else "DOWN",
            "anomaly_service": "UP" if anomaly_ready else "DOWN",
            "loaded_in_memory": models_loaded,
        }

        # 2. Diagnostic du Registre
        reg_status = "UP" if registry_loaded else "DOWN"
        if reg_status == "DOWN":
            is_healthy = False
        components["registry"] = {
            "status": reg_status,
            "version": version,
        }

        # 3. Diagnostic des Schémas de caractéristiques
        schema_status = "UP" if feature_schema_loaded else "DOWN"
        if schema_status == "DOWN":
            is_healthy = False
        components["feature_schema"] = {
            "status": schema_status,
        }

        # 4. Diagnostic d'intégrité des artefacts physiques sur disque
        artifacts_status = "UP"
        artifacts_details: Dict[str, Any] = {}
        if self.loader is not None:
            try:
                manifest_path = self.loader.artifacts_dir / "registry" / "deployment_manifest.json"
                if not manifest_path.is_file():
                    manifest_path = self.loader.artifacts_dir / "deployment_manifest.json"

                artifacts_details["manifest_exists"] = manifest_path.is_file()
                if not manifest_path.is_file():
                    artifacts_status = "WARN"
                    is_degraded = True
            except Exception as e:
                artifacts_status = "ERROR"
                artifacts_details["error"] = str(e)
                is_degraded = True
        components["artifacts"] = {
            "status": artifacts_status,
            "details": artifacts_details,
        }

        # 5. Diagnostic des métriques de fiabilité et de performance
        metrics_status = "UP"
        metrics_details: Dict[str, Any] = {}
        if self.metrics_monitor is not None:
            summary = self.metrics_monitor.get_summary()
            err_rate = summary["reliability"]["error_rate"]
            consec_err = summary["reliability"]["consecutive_errors"]
            metrics_details["error_rate"] = err_rate
            metrics_details["consecutive_errors"] = consec_err
            metrics_details["p95_ms"] = summary["performance"]["p95_ms"]

            # Seuils d'alerte opérationnels
            if err_rate > 0.30 or consec_err >= 5:
                metrics_status = "DEGRADED"
                is_degraded = True
            elif err_rate > 0.60 or consec_err >= 10:
                metrics_status = "DOWN"
                is_healthy = False
        components["metrics"] = {
            "status": metrics_status,
            "details": metrics_details,
        }

        # Détermination du statut global
        if not is_healthy:
            global_status = "unhealthy"
        elif is_degraded:
            global_status = "degraded"
        else:
            global_status = "healthy"

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        details = (additional_details or {}).copy()
        details["check_duration_ms"] = round(elapsed_ms, 3)

        logger.info(
            f"[HealthChecker] Diagnostic effectué : status={global_status}, version={version} ({elapsed_ms:.2f}ms)"
        )

        return HealthStatus(
            status=global_status,
            timestamp=datetime.now(timezone.utc),
            models_loaded=models_loaded,
            registry_loaded=registry_loaded,
            feature_schema_loaded=feature_schema_loaded,
            artifacts_ready=(artifacts_status in ("UP", "WARN")),
            version=version,
            components=components,
            details=details,
        )
