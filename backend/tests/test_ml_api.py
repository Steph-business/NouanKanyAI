"""
tests/test_ml_api.py — Tests d'intégration et d'API pour les routes FastAPI ML (Étape 5).

Valide les endpoints REST versionnés sous /api/v1/ml/* :
- /predict (XGBoost)
- /detect-anomaly (Isolation Forest)
- /health
- /models et /models/{model_name}
- /metrics
- /reload (sécurisé)
- /audit
- Formats d'erreurs standardisés et OpenAPI
"""

from pathlib import Path
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from backend.main import app
from app.api.deps import get_model_manager


@pytest.fixture(scope="module")
def client():
    # Initialiser et charger les modèles pour l'application
    ml_mgr = get_model_manager()
    ml_mgr.load_models()
    with TestClient(app) as test_client:
        yield test_client


# =====================================================================
# Tests: POST /api/v1/ml/predict (Forecasting)
# =====================================================================

class TestPredictEndpoint:
    def test_predict_minimal_input_success(self, client):
        payload = {
            "power_kw": 75.0,
            "temperature_c": 30.0,
        }
        response = client.post("/api/v1/ml/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert "prediction" in data
        assert isinstance(data["prediction"], (int, float))
        assert data["prediction"] >= 0.0
        assert data["unit"] == "kW"
        assert data["model_name"] == "XGBoost_Forecaster"
        assert "metadata" in data
        assert data["metadata"]["feature_count"] == 11

    def test_predict_enriched_input_success(self, client):
        payload = {
            "power_kw": 80.0,
            "temperature_c": 32.0,
            "hour": 15,
            "day_of_week": 2,
            "is_weekend": 0,
            "is_peak_hour": 1,
            "power_kw_lag_1": 78.0,
            "power_kw_lag_6": 72.0,
            "power_kw_lag_24": 65.0,
            "power_rolling_mean": 75.0,
            "power_rolling_std": 4.5,
        }
        response = client.post("/api/v1/ml/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] >= 0.0

    def test_predict_validation_error_missing_power(self, client):
        payload = {"temperature_c": 30.0}
        response = client.post("/api/v1/ml/predict", json=payload)
        assert response.status_code == 422
        error = response.json()
        assert "detail" in error or ("error" in error and error["success"] is False)

    def test_predict_negative_power_rejected(self, client):
        payload = {"power_kw": -10.0, "temperature_c": 25.0}
        response = client.post("/api/v1/ml/predict", json=payload)
        assert response.status_code == 422


# =====================================================================
# Tests: POST /api/v1/ml/detect-anomaly (Anomaly Detection)
# =====================================================================

class TestDetectAnomalyEndpoint:
    def test_detect_normal_observation(self, client):
        payload = {
            "power_kw": 45.0,
            "temperature_c": 35.0,
            "vibration_hz": 2.0,
            "pressure_bar": 1.2,
        }
        response = client.post("/api/v1/ml/detect-anomaly", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert "is_anomaly" in data
        assert isinstance(data["is_anomaly"], bool)
        assert "anomaly_score" in data
        assert "anomaly_probability" in data
        assert "confidence" in data
        assert "severity" in data
        assert data["model_name"] == "IsolationForest_AnomalyDetector"

    def test_detect_extreme_anomaly(self, client):
        payload = {
            "power_kw": 300.0,
            "temperature_c": 110.0,
            "vibration_hz": 80.0,
            "pressure_bar": 10.0,
        }
        response = client.post("/api/v1/ml/detect-anomaly", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["is_anomaly"] is True
        assert data["severity"] in ("faible", "modérée", "critique")

    def test_detect_anomaly_validation_error(self, client):
        payload = {"power_kw": 50.0}  # manque temperature_c, vibration_hz, pressure_bar
        response = client.post("/api/v1/ml/detect-anomaly", json=payload)
        assert response.status_code == 422


# =====================================================================
# Tests: GET /api/v1/ml/health (Health Check)
# =====================================================================

class TestHealthEndpoint:
    def test_health_check_operational(self, client):
        response = client.get("/api/v1/ml/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")
        assert data["models_loaded"] is True
        assert "components" in data
        assert data["components"]["models"]["status"] == "UP"
        assert data["components"]["registry"]["status"] == "UP"


# =====================================================================
# Tests: GET /api/v1/ml/models & models/{model_name}
# =====================================================================

class TestModelsEndpoints:
    def test_list_models(self, client):
        response = client.get("/api/v1/ml/models")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        model_names = [m["name"] for m in data]
        assert "XGBoost_Forecaster" in model_names
        assert "IsolationForest_AnomalyDetector" in model_names

    def test_get_specific_model_info(self, client):
        response = client.get("/api/v1/ml/models/XGBoost_Forecaster")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "XGBoost_Forecaster"
        assert "version" in data
        assert "features" in data
        assert len(data["features"]) > 0

    def test_get_unknown_model_returns_404(self, client):
        response = client.get("/api/v1/ml/models/Unknown_Model_404")
        assert response.status_code == 404


# =====================================================================
# Tests: GET /api/v1/ml/metrics
# =====================================================================

class TestMetricsEndpoint:
    def test_get_metrics_dashboard(self, client):
        # Exécuter une inférence pour alimenter les métriques
        client.post("/api/v1/ml/predict", json={"power_kw": 50.0, "temperature_c": 25.0})

        response = client.get("/api/v1/ml/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "health" in data
        assert "runtime_metrics" in data
        assert "training_metrics" in data
        assert "audit_summary" in data


# =====================================================================
# Tests: POST /api/v1/ml/reload (Security & Hot Reload)
# =====================================================================

class TestReloadEndpoint:
    def test_reload_unauthorized_without_token(self, client):
        response = client.post("/api/v1/ml/reload")
        assert response.status_code == 401

    def test_reload_forbidden_with_wrong_token(self, client):
        response = client.post(
            "/api/v1/ml/reload", headers={"X-API-Key": "invalid_wrong_token_123"}
        )
        assert response.status_code == 403

    def test_reload_success_with_valid_key(self, client):
        response = client.post(
            "/api/v1/ml/reload", headers={"X-API-Key": "dev-admin-key"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reloaded"
        assert "version" in data
        assert len(data["active_models"]) >= 2

    def test_reload_success_with_bearer_token(self, client):
        response = client.post(
            "/api/v1/ml/reload", headers={"Authorization": "Bearer dev-admin-key"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reloaded"


# =====================================================================
# Tests: GET /api/v1/ml/audit
# =====================================================================

class TestAuditEndpoint:
    def test_get_audit_logs(self, client):
        client.post("/api/v1/ml/predict", json={"power_kw": 60.0, "temperature_c": 25.0})
        response = client.get("/api/v1/ml/audit?limit=10")
        assert response.status_code == 200
        records = response.json()
        assert isinstance(records, list)
        assert len(records) > 0
        assert "request_id" in records[0]
        assert "operation" in records[0]
        assert "status" in records[0]


# =====================================================================
# Tests: OpenAPI Documentation
# =====================================================================

class TestOpenAPIDoc:
    def test_openapi_schema_contains_ml_routes(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        paths = schema.get("paths", {})
        assert "/api/v1/ml/predict" in paths
        assert "/api/v1/ml/detect-anomaly" in paths
        assert "/api/v1/ml/health" in paths
        assert "/api/v1/ml/models" in paths
        assert "/api/v1/ml/models/{model_name}" in paths
        assert "/api/v1/ml/metrics" in paths
        assert "/api/v1/ml/reload" in paths
        assert "/api/v1/ml/audit" in paths
