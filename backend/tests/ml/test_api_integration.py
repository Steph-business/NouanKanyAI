"""
backend/tests/ml/test_api_integration.py — Tests d'intégration FastAPI pour les routes versionnées /api/v1/ml/*.

Valide les contrats d'entrée/sortie, les codes de statut HTTP (200, 401, 403, 404, 422),
la sécurité du rechargement et le format standardisé des réponses d'erreur.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from app.api.deps import get_model_manager


@pytest.fixture(scope="module")
def client():
    mgr = get_model_manager()
    mgr.load_models()
    with TestClient(app) as test_client:
        yield test_client


class TestMLAPIIntegrationSuite:
    """Suite de tests d'intégration pour l'API REST ML versionnée."""

    def test_predict_endpoint_success(self, client):
        """Vérifie la réponse nominale du endpoint POST /api/v1/ml/predict."""
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

    def test_predict_endpoint_validation_error_on_invalid_type(self, client):
        """Vérifie le retour 422 en cas d'envoi de type invalide."""
        payload = {
            "power_kw": "texte_invalide",
        }
        response = client.post("/api/v1/ml/predict", json=payload)
        assert response.status_code == 422

    def test_detect_anomaly_endpoint_success(self, client):
        """Vérifie la réponse nominale du endpoint POST /api/v1/ml/detect-anomaly."""
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
        assert data["severity"] in ["normal", "faible", "modérée", "critique"]
        assert data["model_name"] == "IsolationForest_AnomalyDetector"

    def test_health_endpoint(self, client):
        """Vérifie le diagnostic complet du endpoint GET /api/v1/ml/health."""
        response = client.get("/api/v1/ml/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert data["models_loaded"] is True
        assert "components" in data
        assert data["components"]["models"]["status"] == "UP"

    def test_models_list_and_details_endpoints(self, client):
        """Vérifie la consultation du registre GET /api/v1/ml/models et des détails par modèle."""
        response = client.get("/api/v1/ml/models")
        assert response.status_code == 200
        models = response.json()
        assert isinstance(models, list)
        assert len(models) >= 2

        # Détail d'un modèle existant
        detail_res = client.get("/api/v1/ml/models/XGBoost_Forecaster")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["name"] == "XGBoost_Forecaster"

        # Modèle inconnu -> 404
        unknown_res = client.get("/api/v1/ml/models/modele_inexistant")
        assert unknown_res.status_code == 404

    def test_metrics_endpoint(self, client):
        """Vérifie l'exposition de la télémétrie GET /api/v1/ml/metrics."""
        response = client.get("/api/v1/ml/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "health" in data
        assert "runtime_metrics" in data

    def test_reload_security_and_execution(self, client):
        """Vérifie le contrôle d'accès sur le rechargement POST /api/v1/ml/reload."""
        # Sans clé -> 401 ou 403
        unauthorized_res = client.post("/api/v1/ml/reload")
        assert unauthorized_res.status_code in [401, 403]

        # Avec clé API d'administration valide
        authorized_res = client.post(
            "/api/v1/ml/reload",
            headers={"X-API-Key": "dev-admin-key"},
        )
        assert authorized_res.status_code == 200
        data = authorized_res.json()
        assert data["status"] == "reloaded"
        assert "active_models" in data

    def test_audit_logs_endpoint(self, client):
        """Vérifie la consultation de l'historique d'audit GET /api/v1/ml/audit."""
        response = client.get("/api/v1/ml/audit?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
