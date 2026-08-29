"""
backend/tests/ml/test_manager.py — Tests unitaires pour ModelManager.

Vérifie l'orchestration du registre de modèles, l'accès sécurisé aux instances,
le rechargement à chaud (hot-reload) et la résilience en cas de modèle non trouvé.
"""

import pytest
from app.ml.manager import ModelManager
from app.ml.exceptions import ModelNotLoadedError, RegistryError
from app.ml.types import ModelInfo, HealthStatus, PredictionResult, AnomalyResult


class TestModelManager:
    """Suite de tests unitaires pour la façade ModelManager."""

    @pytest.fixture(autouse=True)
    def setup_manager(self):
        self.manager = ModelManager()
        self.manager.load_models()

    def test_manager_initialization_and_loading(self):
        """Vérifie que le manager initialise correctement les modèles au démarrage."""
        assert self.manager._is_loaded is True
        models = self.manager.list_models()
        assert len(models) >= 2
        model_names = [m.name for m in models]
        assert "XGBoost_Forecaster" in model_names
        assert "IsolationForest_AnomalyDetector" in model_names

    def test_get_model_info_valid(self):
        """Vérifie la récupération des métadonnées d'un modèle existant."""
        info = self.manager.get_model_info("XGBoost_Forecaster")
        assert isinstance(info, ModelInfo)
        assert info.name == "XGBoost_Forecaster"
        assert info.model_type == "XGBoost"

    def test_get_model_info_invalid_raises_error(self):
        """Vérifie qu'un modèle inconnu lève une exception RegistryError ou ModelNotLoadedError."""
        with pytest.raises((RegistryError, ModelNotLoadedError)):
            self.manager.get_model_info("modele_inexistant_xyz")

    def test_predict_through_manager(self):
        """Vérifie la réalisation d'une prédiction énergétique via la façade manager."""
        payload = {
            "power_kw": 18.0,
            "power_kw_lag_1": 17.5,
            "power_kw_lag_6": 17.0,
            "power_kw_lag_24": 16.5,
            "power_rolling_mean": 17.2,
            "power_rolling_std": 0.5,
            "hour": 14,
            "day_of_week": 2,
            "is_weekend": 0,
            "is_peak_hour": 1,
            "temperature_c": 28.0,
        }
        result = self.manager.predict(payload)
        assert isinstance(result, PredictionResult)
        assert result.predicted_value > 0

    def test_detect_anomaly_through_manager(self):
        """Vérifie la réalisation d'une détection d'anomalie via la façade manager."""
        payload = {
            "power_kw": 20.0,
            "temperature_c": 30.0,
            "vibration_hz": 12.0,
            "pressure_bar": 2.1,
            "power_rolling_std": 0.4,
            "consumption_delta": 0.2,
            "hour": 15,
        }
        result = self.manager.detect_anomaly(payload)
        assert isinstance(result, AnomalyResult)
        assert isinstance(result.is_anomaly, bool)

    def test_health_check_returns_valid_health_status(self):
        """Vérifie que health_check produit un rapport de santé conforme."""
        health = self.manager.health_check()
        assert isinstance(health, HealthStatus)
        assert health.status in ["healthy", "degraded", "unhealthy"]
        assert health.models_loaded is True

    def test_get_metrics_structure(self):
        """Vérifie que get_metrics retourne les statistiques d'inférence et de latence."""
        metrics = self.manager.get_metrics()
        assert isinstance(metrics, dict)
        assert "health" in metrics or "runtime_metrics" in metrics or len(metrics) > 0

    def test_reload_models_preserves_stability(self):
        """Vérifie que le rechargement à chaud (reload_models) s'exécute sans interruption."""
        self.manager.reload_models()
        assert self.manager._is_loaded is True
        
        info = self.manager.get_model_info("XGBoost_Forecaster")
        assert info is not None
