"""
app/ml/metrics.py — Modèle et utilitaires de gestion des métriques de performance.
"""

import logging
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("nouankany.ml")


class PerformanceMetrics(BaseModel):
    """
    Structure unifiée des métriques de performance des modèles d'IA.
    """

    r2_score: Optional[float] = Field(
        default=None, description="Coefficient de détermination R2 (XGBoost)"
    )
    mae: Optional[float] = Field(
        default=None, description="Erreur Absolue Moyenne (MAE)"
    )
    rmse: Optional[float] = Field(
        default=None, description="Racine de l'Erreur Quadratique Moyenne (RMSE)"
    )
    f1_score: Optional[float] = Field(
        default=None, description="Score F1 pour la détection d'anomalies"
    )
    contamination: Optional[float] = Field(
        default=None, description="Taux de contamination configuré"
    )
    status: str = Field(
        default="UNKNOWN", description="Statut du Quality Gate pour ces métriques"
    )


class ModelMetricsEvaluator:
    """
    Évaluateur et formateur des métriques de performance issues des model cards et du registre.
    """

    @staticmethod
    def parse_metrics(raw_metrics: Dict[str, Any]) -> PerformanceMetrics:
        """
        Extrait et normalise les métriques brutes d'un modèle.

        :param raw_metrics: Dictionnaire brut contenant les métriques.
        :return: Instance de `PerformanceMetrics`.
        """
        return PerformanceMetrics(
            r2_score=raw_metrics.get("r2_score") or raw_metrics.get("r2"),
            mae=raw_metrics.get("mae"),
            rmse=raw_metrics.get("rmse"),
            f1_score=raw_metrics.get("f1_score"),
            contamination=raw_metrics.get("contamination_parameter")
            or raw_metrics.get("contamination"),
            status=raw_metrics.get("status", "PASS"),
        )

    @staticmethod
    def format_summary(
        forecasting_metrics: Dict[str, Any], anomaly_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Génère un dictionnaire synthétique des métriques pour l'ensemble de la couche ML.

        :param forecasting_metrics: Métriques du modèle XGBoost.
        :param anomaly_metrics: Métriques du modèle Isolation Forest.
        :return: Résumé formaté.
        """
        forecasting_parsed = ModelMetricsEvaluator.parse_metrics(forecasting_metrics)
        anomaly_parsed = ModelMetricsEvaluator.parse_metrics(anomaly_metrics)

        return {
            "forecasting": forecasting_parsed.model_dump(exclude_none=True),
            "anomaly_detection": anomaly_parsed.model_dump(exclude_none=True),
        }
