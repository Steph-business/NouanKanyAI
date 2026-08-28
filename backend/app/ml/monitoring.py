"""
app/ml/monitoring.py — Suivi en temps réel des métriques d'inférence ML.
"""

from datetime import datetime, timezone
import logging
import threading
from typing import Any, Dict, List, Optional

logger = logging.getLogger("nouankany.ml")


class MLInferenceMetrics:
    """
    Collecteur et agrégateur de métriques d'inférence en temps réel pour la couche ML.
    Suit la latence, le débit de prédictions, le comptage des anomalies, le taux d'erreur,
    la version active des modèles et l'uptime global.
    """

    def __init__(self) -> None:
        """
        Initialise le moniteur de métriques.
        """
        self._lock = threading.Lock()

        # Compteurs généraux
        self._prediction_count: int = 0
        self._anomaly_count: int = 0
        self._error_count: int = 0

        # Latences d'exécution (en millisecondes)
        self._total_execution_time_ms: float = 0.0
        self._max_execution_time_ms: Optional[float] = None
        self._min_execution_time_ms: Optional[float] = None

        # Métadonnées de session
        self._start_time: datetime = datetime.now(timezone.utc)
        self._last_loaded_at: Optional[datetime] = None
        self._model_versions: Dict[str, str] = {}

        logger.debug("[MLInferenceMetrics] Moniteur de métriques d'inférence initialisé.")

    def set_loaded_info(self, versions: Dict[str, str]) -> None:
        """
        Enregistre les informations du dernier chargement de modèles.

        :param versions: Dictionnaire associant le nom du modèle à sa version.
        """
        with self._lock:
            self._last_loaded_at = datetime.now(timezone.utc)
            self._model_versions = versions.copy()
        logger.debug(
            f"[MLInferenceMetrics] Informations de chargement mises à jour : {versions}"
        )

    def record_inference(
        self, execution_time_ms: float, is_anomaly: bool = False
    ) -> None:
        """
        Enregistre le résultat d'une inférence réussie.

        :param execution_time_ms: Durée d'inférence en millisecondes.
        :param is_anomaly: Vrai si une anomalie a été détectée.
        """
        with self._lock:
            self._prediction_count += 1
            if is_anomaly:
                self._anomaly_count += 1

            self._total_execution_time_ms += execution_time_ms

            if (
                self._max_execution_time_ms is None
                or execution_time_ms > self._max_execution_time_ms
            ):
                self._max_execution_time_ms = execution_time_ms

            if (
                self._min_execution_time_ms is None
                or execution_time_ms < self._min_execution_time_ms
            ):
                self._min_execution_time_ms = execution_time_ms

    def record_error(self) -> None:
        """
        Enregistre l'occurrence d'une erreur d'inférence.
        """
        with self._lock:
            self._error_count += 1
        logger.warning("[MLInferenceMetrics] Une erreur d'inférence a été comptabilisée.")

    @property
    def avg_execution_time_ms(self) -> float:
        """
        Calcule le temps d'exécution moyen.
        """
        with self._lock:
            if self._prediction_count == 0:
                return 0.0
            return self._total_execution_time_ms / self._prediction_count

    @property
    def error_rate(self) -> float:
        """
        Calcule le taux d'erreur cumulé.
        """
        with self._lock:
            total_requests = self._prediction_count + self._error_count
            if total_requests == 0:
                return 0.0
            return self._error_count / total_requests

    @property
    def uptime_seconds(self) -> float:
        """
        Retourne la durée de fonctionnement du système en secondes.
        """
        now = datetime.now(timezone.utc)
        return (now - self._start_time).total_seconds()

    def get_summary(self) -> Dict[str, Any]:
        """
        Génère un résumé complet et structuré des métriques collectées.

        :return: Dictionnaire synthétique.
        """
        with self._lock:
            avg_time = (
                (self._total_execution_time_ms / self._prediction_count)
                if self._prediction_count > 0
                else 0.0
            )
            total_req = self._prediction_count + self._error_count
            err_rate = (self._error_count / total_req) if total_req > 0 else 0.0

            return {
                "prediction_count": self._prediction_count,
                "anomaly_count": self._anomaly_count,
                "error_count": self._error_count,
                "error_rate": round(err_rate, 4),
                "avg_execution_time_ms": round(avg_time, 2),
                "max_execution_time_ms": (
                    round(self._max_execution_time_ms, 2)
                    if self._max_execution_time_ms is not None
                    else 0.0
                ),
                "min_execution_time_ms": (
                    round(self._min_execution_time_ms, 2)
                    if self._min_execution_time_ms is not None
                    else 0.0
                ),
                "active_model_versions": self._model_versions,
                "last_loaded_at": (
                    self._last_loaded_at.isoformat()
                    if self._last_loaded_at
                    else None
                ),
                "uptime_seconds": round(self.uptime_seconds, 2),
            }
