"""
app/ml/health.py — Contrôleur d'état de santé de la couche ML.
"""

import logging
from typing import Any, Dict

from app.ml.types import HealthStatus

logger = logging.getLogger("nouankany.ml")


class HealthChecker:
    """
    Composant responsable des diagnostics de disponibilité et de santé
    de la couche Machine Learning.
    """

    def check(
        self,
        models_loaded: bool,
        registry_loaded: bool,
        feature_schema_loaded: bool,
        version: str,
        additional_details: Dict[str, Any] | None = None,
    ) -> HealthStatus:
        """
        Évalue et retourne l'état de santé global.

        :param models_loaded: Vrai si les modèles joblib sont préchargés.
        :param registry_loaded: Vrai si le registre est accessible.
        :param feature_schema_loaded: Vrai si le schéma des caractéristiques est chargé.
        :param version: Version active courante.
        :param additional_details: Informations de diagnostic complémentaires.
        :return: Instance typée `HealthStatus`.
        """
        all_ready = models_loaded and registry_loaded and feature_schema_loaded

        if all_ready:
            status_str = "healthy"
        elif models_loaded or registry_loaded:
            status_str = "degraded"
        else:
            status_str = "unhealthy"

        logger.info(
            f"[HealthChecker] Diagnostic effectué : status={status_str}, version={version}"
        )

        return HealthStatus(
            status=status_str,
            models_loaded=models_loaded,
            registry_loaded=registry_loaded,
            feature_schema_loaded=feature_schema_loaded,
            version=version,
            details=additional_details or {},
        )
