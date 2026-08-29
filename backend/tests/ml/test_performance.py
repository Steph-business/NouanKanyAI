"""
backend/tests/ml/test_performance.py — Tests de performance et respect des objectifs de latence (SLA / SLO).

Vérifie que les modèles XGBoost et Isolation Forest effectuent leurs inférences
dans un temps maximal strictement inférieur au seuil configurable (ML_MAX_LATENCY_MS).
"""

import os
import time
import pytest
from app.ml.manager import ModelManager

# Seuil maximal de latence admissible par défaut (en millisecondes)
DEFAULT_MAX_LATENCY_MS = 250.0
MAX_LATENCY_MS = float(os.environ.get("ML_MAX_LATENCY_MS", DEFAULT_MAX_LATENCY_MS))


class TestMLPerformanceSLO:
    """Suite de validation des exigences de réactivité et de latence pour le sous-système ML."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.manager = ModelManager()
        self.manager.load_models()

    def test_forecasting_latency_under_threshold(self):
        """Vérifie que le temps d'inférence de prévision reste strictement inférieur au seuil configuré."""
        sample_input = {
            "power_kw": 20.0,
            "power_kw_lag_1": 19.5,
            "power_kw_lag_6": 19.0,
            "power_kw_lag_24": 18.5,
            "power_rolling_mean": 19.2,
            "power_rolling_std": 0.4,
            "hour": 14,
            "day_of_week": 2,
            "is_weekend": 0,
            "is_peak_hour": 1,
            "temperature_c": 28.5,
        }
        
        # Warm-up (2 passes)
        _ = self.manager.predict(sample_input)
        _ = self.manager.predict(sample_input)

        # Mesure d'inférence
        start = time.perf_counter()
        result = self.manager.predict(sample_input)
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        assert result.metadata.execution_time_ms <= MAX_LATENCY_MS, (
            f"La latence d'inférence ({result.metadata.execution_time_ms:.2f}ms) dépasse le seuil de {MAX_LATENCY_MS}ms."
        )
        assert elapsed_ms <= MAX_LATENCY_MS * 2.0

    def test_anomaly_detection_latency_under_threshold(self):
        """Vérifie que le temps de détection d'anomalie reste strictement inférieur au seuil configuré."""
        sample_input = {
            "power_kw": 21.0,
            "temperature_c": 30.0,
            "vibration_hz": 9.5,
            "pressure_bar": 2.0,
            "power_rolling_std": 0.4,
            "consumption_delta": 0.1,
            "hour": 10,
        }

        # Warm-up (2 passes)
        _ = self.manager.detect_anomaly(sample_input)
        _ = self.manager.detect_anomaly(sample_input)

        # Mesure d'inférence
        start = time.perf_counter()
        result = self.manager.detect_anomaly(sample_input)
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        assert result.metadata.execution_time_ms <= MAX_LATENCY_MS, (
            f"La latence d'anomalie ({result.metadata.execution_time_ms:.2f}ms) dépasse le seuil de {MAX_LATENCY_MS}ms."
        )
        assert elapsed_ms <= MAX_LATENCY_MS * 2.0

    def test_batch_sequential_inference_throughput(self):
        """Vérifie la stabilité de la latence moyenne sur une série séquentielle d'inférences."""
        sample_input = {
            "power_kw": 18.0,
            "power_kw_lag_1": 18.0,
            "power_kw_lag_6": 17.5,
            "power_kw_lag_24": 18.2,
            "power_rolling_mean": 17.8,
            "power_rolling_std": 0.4,
            "hour": 11,
            "day_of_week": 1,
            "is_weekend": 0,
            "is_peak_hour": 1,
            "temperature_c": 27.0,
        }
        iterations = 15
        latencies = []

        # Warm-up
        _ = self.manager.predict(sample_input)

        for _ in range(iterations):
            start = time.perf_counter()
            _ = self.manager.predict(sample_input)
            latencies.append((time.perf_counter() - start) * 1000.0)

        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency <= MAX_LATENCY_MS, (
            f"La latence moyenne ({avg_latency:.2f}ms) sur {iterations} itérations dépasse {MAX_LATENCY_MS}ms."
        )
