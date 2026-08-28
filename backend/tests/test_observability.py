from datetime import datetime, timezone
from pathlib import Path
import sys
import time
import uuid
import pytest

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.ml.audit import AuditLogger, AuditRecord
from app.ml.events import MLEvent, MLEventDispatcher, MLEventType
from app.ml.health import HealthChecker
from app.ml.manager import ModelManager
from app.ml.metrics_service import MetricsService
from app.ml.monitoring import MLInferenceMetrics
from app.ml.types import HealthStatus


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def metrics_collector():
    return MLInferenceMetrics(latency_window_size=100)


@pytest.fixture
def audit_logger():
    return AuditLogger(max_buffer_size=100)


@pytest.fixture
def event_bus():
    return MLEventDispatcher(max_history=100)


@pytest.fixture
def loaded_manager():
    manager = ModelManager()
    manager.load_models()
    return manager


# =====================================================================
# Tests: MLInferenceMetrics
# =====================================================================

class TestMLInferenceMetrics:
    def test_record_inference_and_latency_distribution(self, metrics_collector):
        latencies = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        for lat in latencies:
            metrics_collector.record_inference(
                execution_time_ms=lat, is_anomaly=False, model_name="XGBoost_Forecaster"
            )

        summary = metrics_collector.get_summary()
        assert summary["usage"]["prediction_count"] == 10
        assert summary["usage"]["anomaly_count"] == 0
        assert summary["performance"]["avg_execution_time_ms"] == 55.0
        assert summary["performance"]["min_execution_time_ms"] == 10.0
        assert summary["performance"]["max_execution_time_ms"] == 100.0
        assert summary["usage"]["by_model"]["XGBoost_Forecaster"] == 10

        percentiles = metrics_collector.get_latency_percentiles()
        assert 45.0 <= percentiles["p50"] <= 65.0
        assert percentiles["p95"] >= 90.0

    def test_record_error_and_consecutive_tracking(self, metrics_collector):
        metrics_collector.record_inference(15.0)
        metrics_collector.record_error("Validation failed", is_validation=True)
        metrics_collector.record_error("Model timeout", is_validation=False)

        summary = metrics_collector.get_summary()
        assert summary["reliability"]["error_count"] == 2
        assert summary["reliability"]["validation_error_count"] == 1
        assert summary["reliability"]["consecutive_errors"] == 2
        assert summary["reliability"]["last_error_message"] == "Model timeout"
        assert 0.0 < summary["reliability"]["error_rate"] <= 1.0

        # Une inférence réussie remet les erreurs consécutives à zéro
        metrics_collector.record_inference(20.0)
        updated = metrics_collector.get_summary()
        assert updated["reliability"]["consecutive_errors"] == 0
        assert updated["reliability"]["max_consecutive_errors"] == 2

    def test_reset_metrics(self, metrics_collector):
        metrics_collector.record_inference(50.0)
        metrics_collector.record_error("Erreur")
        metrics_collector.reset()

        summary = metrics_collector.get_summary()
        assert summary["usage"]["prediction_count"] == 0
        assert summary["reliability"]["error_count"] == 0


# =====================================================================
# Tests: AuditLogger
# =====================================================================

class TestAuditLogger:
    def test_log_inference_and_query(self, audit_logger):
        req_id = str(uuid.uuid4())
        record = audit_logger.log_inference(
            request_id=req_id,
            operation="forecasting",
            model_name="XGBoost_Forecaster",
            model_version="2.0.0",
            execution_time_ms=25.4,
            input_summary={"power_kw": 80.0},
            output_summary={"predicted_value": 82.5},
            input_hash="hash_12345",
            status="SUCCESS",
        )

        assert isinstance(record, AuditRecord)
        assert record.request_id == req_id
        assert record.status == "SUCCESS"

        records = audit_logger.get_records(limit=10, model_name="XGBoost_Forecaster")
        assert len(records) == 1
        assert records[0].request_id == req_id

    def test_audit_summary_aggregation(self, audit_logger):
        audit_logger.log_inference(
            request_id="r1",
            operation="forecasting",
            model_name="XGBoost_Forecaster",
            model_version="2.0.0",
            execution_time_ms=10.0,
            input_summary={},
            output_summary={},
            status="SUCCESS",
        )
        audit_logger.log_inference(
            request_id="r2",
            operation="anomaly_detection",
            model_name="IsolationForest_AnomalyDetector",
            model_version="2.0.0",
            execution_time_ms=20.0,
            input_summary={},
            output_summary={},
            status="ERROR",
            error_message="Panne",
        )

        summary = audit_logger.get_summary()
        assert summary["total_audited_transactions"] == 2
        assert summary["by_status"]["SUCCESS"] == 1
        assert summary["by_status"]["ERROR"] == 1
        assert summary["by_operation"]["forecasting"] == 1
        assert summary["by_operation"]["anomaly_detection"] == 1
        assert summary["avg_latency_ms"] == 15.0


# =====================================================================
# Tests: MLEventDispatcher
# =====================================================================

class TestMLEventDispatcher:
    def test_dispatch_and_subscribe(self, event_bus):
        received_events = []

        def on_prediction_success(event: MLEvent):
            received_events.append(event)

        event_bus.subscribe(MLEventType.PREDICTION_SUCCESS, on_prediction_success)

        event = event_bus.dispatch(
            event_type=MLEventType.PREDICTION_SUCCESS,
            request_id="req_999",
            model_name="XGBoost_Forecaster",
            payload={"predicted_value": 75.2},
        )

        assert len(received_events) == 1
        assert received_events[0].request_id == "req_999"
        assert received_events[0].payload["predicted_value"] == 75.2

    def test_event_history_and_filters(self, event_bus):
        event_bus.dispatch(MLEventType.MODEL_LOADED, payload={"status": "OK"})
        event_bus.dispatch(MLEventType.PREDICTION_ERROR, payload={"err": "Timeout"})

        history = event_bus.get_recent_events(limit=10)
        assert len(history) == 2

        filtered = event_bus.get_recent_events(event_type=MLEventType.PREDICTION_ERROR)
        assert len(filtered) == 1
        assert filtered[0].event_type == MLEventType.PREDICTION_ERROR


# =====================================================================
# Tests: HealthChecker
# =====================================================================

class TestHealthChecker:
    def test_healthy_status_evaluation(self):
        checker = HealthChecker()
        status = checker.check(
            models_loaded=True,
            registry_loaded=True,
            feature_schema_loaded=True,
            version="2.0.0",
            forecasting_ready=True,
            anomaly_ready=True,
        )
        assert isinstance(status, HealthStatus)
        assert status.status == "healthy"
        assert status.models_loaded is True
        assert status.components["models"]["status"] == "UP"

    def test_unhealthy_when_models_down(self):
        checker = HealthChecker()
        status = checker.check(
            models_loaded=False,
            registry_loaded=True,
            feature_schema_loaded=True,
            version="2.0.0",
            forecasting_ready=False,
            anomaly_ready=False,
        )
        assert status.status == "unhealthy"
        assert status.components["models"]["status"] == "DOWN"


# =====================================================================
# Tests: MetricsService
# =====================================================================

class TestMetricsService:
    def test_dashboard_summary_generation(self, loaded_manager):
        service = loaded_manager.metrics_service
        loaded_manager.predict({"power_kw": 55.0, "temperature_c": 30.0})
        loaded_manager.detect_anomaly({
            "power_kw": 55.0,
            "temperature_c": 30.0,
            "vibration_hz": 1.5,
            "pressure_bar": 1.2,
        })

        dashboard = service.get_dashboard_summary(models_loaded=True, version="2.0.0")
        assert "health" in dashboard
        assert "runtime_metrics" in dashboard
        assert "training_metrics" in dashboard
        assert "audit_summary" in dashboard
        assert dashboard["runtime_metrics"]["usage"]["prediction_count"] >= 2
        assert dashboard["audit_summary"]["total_audited_transactions"] >= 2

    def test_latency_distribution_service(self, loaded_manager):
        service = loaded_manager.metrics_service
        dist = service.get_latency_distribution()
        assert "p50" in dist
        assert "p95" in dist
        assert "p99" in dist
        assert "avg_ms" in dist


# =====================================================================
# Tests: End-to-End Observability in ModelManager
# =====================================================================

class TestEndToEndObservability:
    def test_inference_triggers_audit_and_events(self, loaded_manager):
        events_caught = []

        def capture_event(event: MLEvent):
            events_caught.append(event)

        loaded_manager.event_dispatcher.subscribe(None, capture_event)

        custom_req_id = f"test-req-{uuid.uuid4()}"
        res = loaded_manager.predict(
            {"power_kw": 70.0, "temperature_c": 28.0}, request_id=custom_req_id
        )

        assert res.request_id == custom_req_id

        # Vérification des événements capturés
        event_types = [e.event_type for e in events_caught]
        assert MLEventType.PREDICTION_REQUESTED in event_types
        assert MLEventType.PREDICTION_SUCCESS in event_types

        # Vérification du journal d'audit
        audit_records = loaded_manager.audit_logger.get_records(request_id=custom_req_id)
        assert len(audit_records) == 1
        assert audit_records[0].status == "SUCCESS"
        assert audit_records[0].operation == "forecasting"
        assert audit_records[0].model_name == "XGBoost_Forecaster"

    def test_anomaly_detection_triggers_appropriate_event(self, loaded_manager):
        events_caught = []

        def capture_event(event: MLEvent):
            events_caught.append(event)

        loaded_manager.event_dispatcher.subscribe(None, capture_event)

        custom_req_id = f"test-anom-{uuid.uuid4()}"
        res = loaded_manager.detect_anomaly(
            {
                "power_kw": 250.0,
                "temperature_c": 95.0,
                "vibration_hz": 60.0,
                "pressure_bar": 6.0,
            },
            request_id=custom_req_id,
        )

        assert res.request_id == custom_req_id
        audit_records = loaded_manager.audit_logger.get_records(request_id=custom_req_id)
        assert len(audit_records) == 1
        assert audit_records[0].operation == "anomaly_detection"
