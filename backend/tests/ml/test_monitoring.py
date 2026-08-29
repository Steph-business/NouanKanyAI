"""
backend/tests/ml/test_monitoring.py — Tests unitaires pour l'observabilité, les métriques et l'audit ML.

Vérifie MLInferenceMetrics (latences percentiles p50/p95/p99), AuditLogger (tampon et JSONL),
HealthChecker (état de santé des composants) et MLEventDispatcher (événements internes).
"""

import threading
import time
import pytest
from app.ml.monitoring import MLInferenceMetrics
from app.ml.audit import AuditLogger, AuditRecord
from app.ml.health import HealthChecker
from app.ml.events import MLEventDispatcher, MLEventType, MLEvent
from app.ml.manager import ModelManager


class TestMonitoringAndObservabilitySuite:
    """Suite de tests unitaires pour l'observabilité et le monitoring ML."""

    def test_metrics_record_and_percentiles(self):
        """Vérifie le calcul correct des percentiles p50, p95, p99 et des statistiques de latence."""
        metrics = MLInferenceMetrics(latency_window_size=100)
        
        # Enregistrement d'une série de latences connues : 10ms à 100ms
        for lat in range(10, 110, 10):
            metrics.record_inference(
                execution_time_ms=float(lat),
                is_anomaly=False,
                model_name="XGBoost_Forecaster",
            )

        stats = metrics.get_summary()
        assert stats["usage"]["total_requests"] == 10
        assert stats["reliability"]["error_count"] == 0
        assert stats["reliability"]["error_rate"] == 0.0
        assert stats["performance"]["avg_execution_time_ms"] > 0
        assert stats["performance"]["p50_ms"] >= 40.0
        assert stats["performance"]["p95_ms"] >= 90.0
        assert stats["performance"]["p99_ms"] >= 95.0

    def test_metrics_error_tracking(self):
        """Vérifie la comptabilisation des erreurs et le calcul du taux d'échec."""
        metrics = MLInferenceMetrics(latency_window_size=50)
        metrics.record_inference(15.0, is_anomaly=False, model_name="XGBoost_Forecaster")
        metrics.record_error("ValueError: invalid input", model_name="XGBoost_Forecaster")

        stats = metrics.get_summary()
        assert stats["usage"]["total_requests"] == 2
        assert stats["reliability"]["error_count"] == 1
        assert stats["reliability"]["error_rate"] == 0.5

    def test_metrics_thread_safety(self):
        """Vérifie la robustesse multi-thread lors d'appels simultanés."""
        metrics = MLInferenceMetrics(latency_window_size=1000)
        num_threads = 10
        inferences_per_thread = 50

        def worker():
            for _ in range(inferences_per_thread):
                metrics.record_inference(12.5, is_anomaly=False, model_name="XGBoost_Forecaster")

        threads = [threading.Thread(target=worker) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = metrics.get_summary()
        assert stats["usage"]["prediction_count"] == num_threads * inferences_per_thread

    def test_audit_logger_records_and_retrieval(self, tmp_path):
        """Vérifie l'enregistrement des requêtes dans le buffer mémoire et le fichier JSONL."""
        log_file = tmp_path / "test_audit.jsonl"
        audit = AuditLogger(max_buffer_size=100, log_file_path=log_file)

        record = audit.log_inference(
            request_id="req-12345",
            operation="forecasting",
            model_name="XGBoost_Forecaster",
            model_version="v2.0.0",
            execution_time_ms=14.2,
            input_summary={"power_kw": 20.0},
            output_summary={"predicted_kw": 22.5},
            input_hash="abc123def456",
            status="SUCCESS",
        )
        assert record.request_id == "req-12345"

        recent_logs = audit.get_records(limit=10)
        assert len(recent_logs) == 1
        assert recent_logs[0].request_id == "req-12345"
        assert recent_logs[0].status == "SUCCESS"
        assert log_file.exists()

    def test_health_checker_evaluation(self):
        """Vérifie l'évaluation de l'état de santé opérationnel via HealthChecker."""
        manager = ModelManager()
        manager.load_models()
        checker = manager.health_checker

        status = checker.check(
            models_loaded=True,
            registry_loaded=True,
            feature_schema_loaded=True,
            version="2.0.0",
        )
        assert status.status in ["healthy", "degraded", "unhealthy"]
        assert status.models_loaded is True

    def test_event_dispatcher_subscription_and_emission(self):
        """Vérifie l'enregistrement des écouteurs et la distribution d'événements ML."""
        dispatcher = MLEventDispatcher()
        received_events = []

        def sample_listener(event: MLEvent):
            received_events.append(event)

        dispatcher.subscribe(MLEventType.PREDICTION_SUCCESS, sample_listener)
        
        dispatcher.dispatch(
            event_type=MLEventType.PREDICTION_SUCCESS,
            request_id="test-uuid-99",
            model_name="XGBoost_Forecaster",
            payload={"value": 42.0},
        )

        assert len(received_events) == 1
        assert received_events[0].request_id == "test-uuid-99"
