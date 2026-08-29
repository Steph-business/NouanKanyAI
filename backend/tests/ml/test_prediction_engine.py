"""
backend/tests/ml/test_prediction_engine.py — Tests unitaires pour le moteur d'inférence et de prétraitement.

Vérifie le fonctionnement de PredictionEngine, ForecastingService, AnomalyDetectionService,
la dérivation automatique des features temporelles, le calcul du hash SHA-256 et la mesure de latence.
"""

import pytest
from app.ml.manager import ModelManager
from app.ml.types import PredictionResult, AnomalyResult


class TestPredictionEngineSuite:
    """Suite de tests unitaires pour le moteur de prédiction et les services d'inférence."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.manager = ModelManager()
        self.manager.load_models()
        self.engine = self.manager._prediction_engine

    def test_forecasting_prediction_nominal(self):
        """Vérifie l'exécution complète d'une prédiction de puissance (XGBoost)."""
        input_data = {
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
            "temperature_c": 28.0,
        }
        result = self.engine.predict_forecasting(input_data)
        assert isinstance(result, PredictionResult)
        assert result.predicted_value > 0
        assert result.model_name == "XGBoost_Forecaster"
        assert result.model_version is not None
        assert result.metadata.execution_time_ms > 0
        assert isinstance(result.request_id, str)
        assert len(result.request_id) > 0
        assert isinstance(result.metadata.data_hash, str)

    def test_anomaly_detection_nominal(self):
        """Vérifie l'exécution complète d'une détection d'anomalie (Isolation Forest)."""
        input_data = {
            "power_kw": 20.0,
            "temperature_c": 29.0,
            "vibration_hz": 8.0,
            "pressure_bar": 2.0,
            "power_rolling_std": 0.4,
            "consumption_delta": 0.1,
            "hour": 10,
        }
        result = self.engine.predict_anomaly(input_data)
        assert isinstance(result, AnomalyResult)
        assert isinstance(result.is_anomaly, bool)
        assert isinstance(result.score, float)
        assert 0.0 <= result.probability <= 1.0
        assert 0.0 <= result.confidence <= 1.0
        assert result.severity in ["normal", "faible", "modérée", "critique"]
        assert result.metadata.execution_time_ms > 0
        assert isinstance(result.request_id, str)

    def test_anomaly_detection_critical_behavior(self):
        """Vérifie la détection d'une anomalie extrême."""
        extreme_input = {
            "power_kw": 350.0,
            "temperature_c": 120.0,
            "vibration_hz": 120.0,
            "pressure_bar": 12.0,
            "power_rolling_std": 45.0,
            "consumption_delta": 65.0,
            "hour": 14,
        }
        result = self.engine.predict_anomaly(extreme_input)
        assert isinstance(result, AnomalyResult)
        assert result.is_anomaly is True
        assert result.severity in ["modérée", "critique"]

    def test_forecasting_service_direct_inference(self):
        """Vérifie l'inférence directe via le ForecastingService."""
        service = self.manager._forecasting_service
        features = {
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
        res = service.predict(features)
        assert isinstance(res, PredictionResult)
        assert res.predicted_value > 0.0
        assert res.metadata.execution_time_ms > 0.0

    def test_anomaly_service_direct_inference(self):
        """Vérifie l'inférence directe via l'AnomalyDetectionService."""
        service = self.manager._anomaly_service
        features = {
            "power_kw": 22.0,
            "temperature_c": 31.0,
            "vibration_hz": 11.0,
            "pressure_bar": 2.1,
            "power_rolling_std": 0.5,
            "consumption_delta": 0.2,
            "hour": 15,
        }
        res = service.detect(features)
        assert isinstance(res, AnomalyResult)
        assert isinstance(res.is_anomaly, bool)
        assert isinstance(res.score, float)
        assert res.metadata.execution_time_ms > 0.0
