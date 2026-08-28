"""
app/ml/monitoring.py — Suivi en temps réel des métriques d'inférence, performance et fiabilité ML.
"""

from datetime import datetime, timezone
import logging
import threading
from typing import Any, Dict, List, Optional
import numpy as np

logger = logging.getLogger("nouankany.ml")


class MLInferenceMetrics:
    """
    Collecteur et agrégateur central de métriques d'inférence en temps réel pour la couche ML.
    Suit l'utilisation, les distributions de latence (p50, p95, p99), le comptage des anomalies,
    la fiabilité, le taux d'erreur et les versions actives des modèles.
    """

    def __init__(self, latency_window_size: int = 1000) -> None:
        """
        Initialise le moniteur de métriques d'inférence.

        :param latency_window_size: Taille de la fenêtre glissante pour le calcul des percentiles.
        """
        self._lock = threading.RLock()
        self._latency_window_size = latency_window_size

        # Compteurs généraux d'utilisation
        self._prediction_count: int = 0
        self._anomaly_count: int = 0
        self._normal_count: int = 0
        self._error_count: int = 0
        self._validation_error_count: int = 0

        # Suivi par modèle
        self._model_inference_counts: Dict[str, int] = {}
        self._model_error_counts: Dict[str, int] = {}
        self._model_latencies: Dict[str, List[float]] = {}

        # Fenêtre glissante pour latences (millisecondes)
        self._recent_latencies: List[float] = []
        self._total_execution_time_ms: float = 0.0
        self._max_execution_time_ms: Optional[float] = None
        self._min_execution_time_ms: Optional[float] = None

        # Suivi des erreurs et fiabilité
        self._consecutive_errors: int = 0
        self._max_consecutive_errors: int = 0
        self._last_error_at: Optional[datetime] = None
        self._last_error_message: Optional[str] = None

        # Fenêtre temporelle pour débit (inferences / timestamps récents)
        self._recent_timestamps: List[datetime] = []

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
        self,
        execution_time_ms: float,
        is_anomaly: bool = False,
        model_name: Optional[str] = None,
    ) -> None:
        """
        Enregistre le résultat d'une inférence réussie.

        :param execution_time_ms: Durée d'inférence en millisecondes.
        :param is_anomaly: Vrai si une anomalie a été détectée.
        :param model_name: Nom optionnel du modèle concerné.
        """
        now = datetime.now(timezone.utc)
        with self._lock:
            self._prediction_count += 1
            if is_anomaly:
                self._anomaly_count += 1
            else:
                self._normal_count += 1

            self._consecutive_errors = 0
            self._total_execution_time_ms += execution_time_ms

            # Suivi des bornes min / max
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

            # Fenêtre glissante générale
            self._recent_latencies.append(execution_time_ms)
            if len(self._recent_latencies) > self._latency_window_size:
                self._recent_latencies.pop(0)

            # Fenêtre glissante pour le débit (dernière heure)
            self._recent_timestamps.append(now)
            cutoff = now.timestamp() - 3600.0
            self._recent_timestamps = [
                ts for ts in self._recent_timestamps if ts.timestamp() > cutoff
            ]

            # Suivi spécifique par modèle
            if model_name:
                self._model_inference_counts[model_name] = (
                    self._model_inference_counts.get(model_name, 0) + 1
                )
                if model_name not in self._model_latencies:
                    self._model_latencies[model_name] = []
                self._model_latencies[model_name].append(execution_time_ms)
                if len(self._model_latencies[model_name]) > 500:
                    self._model_latencies[model_name].pop(0)

    def record_error(
        self,
        error_message: Optional[str] = None,
        is_validation: bool = False,
        model_name: Optional[str] = None,
    ) -> None:
        """
        Enregistre l'occurrence d'une erreur d'inférence ou de validation.

        :param error_message: Message descriptif de l'erreur.
        :param is_validation: Vrai si l'erreur provient de la validation des caractéristiques.
        :param model_name: Nom optionnel du modèle associé.
        """
        now = datetime.now(timezone.utc)
        with self._lock:
            self._error_count += 1
            if is_validation:
                self._validation_error_count += 1

            self._consecutive_errors += 1
            if self._consecutive_errors > self._max_consecutive_errors:
                self._max_consecutive_errors = self._consecutive_errors

            self._last_error_at = now
            self._last_error_message = error_message

            if model_name:
                self._model_error_counts[model_name] = (
                    self._model_error_counts.get(model_name, 0) + 1
                )

        logger.warning(
            f"[MLInferenceMetrics] Erreur d'inférence comptabilisée (consécutives: {self._consecutive_errors}, message: {error_message})"
        )

    def get_latency_percentiles(self) -> Dict[str, float]:
        """
        Calcule les percentiles de latence (p50, p95, p99) sur la fenêtre récente.

        :return: Dictionnaire des percentiles en ms.
        """
        with self._lock:
            if not self._recent_latencies:
                return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

            arr = np.array(self._recent_latencies)
            return {
                "p50": round(float(np.percentile(arr, 50)), 2),
                "p95": round(float(np.percentile(arr, 95)), 2),
                "p99": round(float(np.percentile(arr, 99)), 2),
            }

    @property
    def avg_execution_time_ms(self) -> float:
        """
        Calcule le temps d'exécution moyen global.
        """
        with self._lock:
            if self._prediction_count == 0:
                return 0.0
            return self._total_execution_time_ms / self._prediction_count

    @property
    def error_rate(self) -> float:
        """
        Calcule le taux d'erreur cumulé (0.0 à 1.0).
        """
        with self._lock:
            total_requests = self._prediction_count + self._error_count
            if total_requests == 0:
                return 0.0
            return self._error_count / total_requests

    @property
    def success_rate(self) -> float:
        """
        Calcule le taux de succès cumulé (0.0 à 1.0).
        """
        return max(0.0, 1.0 - self.error_rate)

    @property
    def anomaly_rate(self) -> float:
        """
        Calcule la proportion d'anomalies par rapport aux inférences totales.
        """
        with self._lock:
            if self._prediction_count == 0:
                return 0.0
            return self._anomaly_count / self._prediction_count

    @property
    def uptime_seconds(self) -> float:
        """
        Retourne la durée de fonctionnement du système en secondes.
        """
        now = datetime.now(timezone.utc)
        return (now - self._start_time).total_seconds()

    @property
    def requests_last_minute(self) -> int:
        """
        Retourne le nombre de requêtes traitées lors des 60 dernières secondes.
        """
        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - 60.0
        with self._lock:
            return sum(1 for ts in self._recent_timestamps if ts.timestamp() > cutoff)

    def get_summary(self) -> Dict[str, Any]:
        """
        Génère un résumé complet et structuré de l'ensemble des métriques d'observabilité.

        :return: Dictionnaire structuré contenant utilisation, performance, fiabilité et état.
        """
        with self._lock:
            total_req = self._prediction_count + self._error_count
            avg_time = (
                (self._total_execution_time_ms / self._prediction_count)
                if self._prediction_count > 0
                else 0.0
            )
            err_rate = (self._error_count / total_req) if total_req > 0 else 0.0
            anom_rate = (
                (self._anomaly_count / self._prediction_count)
                if self._prediction_count > 0
                else 0.0
            )

            # Calcul des percentiles
            if self._recent_latencies:
                arr = np.array(self._recent_latencies)
                p50 = float(np.percentile(arr, 50))
                p95 = float(np.percentile(arr, 95))
                p99 = float(np.percentile(arr, 99))
            else:
                p50 = p95 = p99 = 0.0

            # Calcul des moyennes par modèle
            by_model_latency: Dict[str, float] = {}
            for m_name, lat_list in self._model_latencies.items():
                if lat_list:
                    by_model_latency[m_name] = round(float(np.mean(lat_list)), 2)

            return {
                "usage": {
                    "total_requests": total_req,
                    "prediction_count": self._prediction_count,
                    "anomaly_count": self._anomaly_count,
                    "normal_count": self._normal_count,
                    "anomaly_rate": round(anom_rate, 4),
                    "requests_last_minute": self.requests_last_minute,
                    "by_model": self._model_inference_counts.copy(),
                },
                "performance": {
                    "avg_execution_time_ms": round(avg_time, 2),
                    "min_execution_time_ms": (
                        round(self._min_execution_time_ms, 2)
                        if self._min_execution_time_ms is not None
                        else 0.0
                    ),
                    "max_execution_time_ms": (
                        round(self._max_execution_time_ms, 2)
                        if self._max_execution_time_ms is not None
                        else 0.0
                    ),
                    "p50_ms": round(p50, 2),
                    "p95_ms": round(p95, 2),
                    "p99_ms": round(p99, 2),
                    "by_model_avg_latency_ms": by_model_latency,
                },
                "reliability": {
                    "error_count": self._error_count,
                    "validation_error_count": self._validation_error_count,
                    "error_rate": round(err_rate, 4),
                    "success_rate": round(max(0.0, 1.0 - err_rate), 4),
                    "consecutive_errors": self._consecutive_errors,
                    "max_consecutive_errors": self._max_consecutive_errors,
                    "last_error_at": (
                        self._last_error_at.isoformat()
                        if self._last_error_at
                        else None
                    ),
                    "last_error_message": self._last_error_message,
                    "by_model_errors": self._model_error_counts.copy(),
                },
                "system": {
                    "active_model_versions": self._model_versions.copy(),
                    "last_loaded_at": (
                        self._last_loaded_at.isoformat()
                        if self._last_loaded_at
                        else None
                    ),
                    "uptime_seconds": round(self.uptime_seconds, 2),
                },
                # Rétrocompatibilité avec les tests existants
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

    def reset(self) -> None:
        """
        Réinitialise les compteurs de métriques.
        """
        with self._lock:
            self._prediction_count = 0
            self._anomaly_count = 0
            self._normal_count = 0
            self._error_count = 0
            self._validation_error_count = 0
            self._consecutive_errors = 0
            self._max_consecutive_errors = 0
            self._total_execution_time_ms = 0.0
            self._max_execution_time_ms = None
            self._min_execution_time_ms = None
            self._recent_latencies.clear()
            self._recent_timestamps.clear()
            self._model_inference_counts.clear()
            self._model_error_counts.clear()
            self._model_latencies.clear()
            self._last_error_at = None
            self._last_error_message = None
            self._start_time = datetime.now(timezone.utc)
