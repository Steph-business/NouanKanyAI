from datetime import datetime, timezone
from pathlib import Path
import sys
import uuid
import numpy as np
import pandas as pd
import pytest

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.ml.anomaly_detector import AnomalyDetectionService
from app.ml.exceptions import (
    FeatureValidationError,
    ModelNotLoadedError,
    PredictionError,
    PreprocessingError,
)
from app.ml.forecasting import ForecastingService
from app.ml.loader import ModelLoader
from app.ml.manager import ModelManager
from app.ml.monitoring import MLInferenceMetrics
from app.ml.predictor import PredictionEngine
from app.ml.preprocessing import (
    ANOMALY_FEATURES,
    FORECASTING_FEATURES,
    FeaturePreprocessor,
    compute_data_hash,
    extract_temporal_features,
)
from app.ml.types import (
    AnomalyResult,
    PredictionMetadata,
    PredictionResult,
)
from app.ml.validators import FeatureValidator


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def sample_schema_v2():
    return {
        "metadata": {"project": "NouanKanyAI", "version": "2.0.0"},
        "features": {
            "power_kw": {"type": "float64", "min": 0.0, "max": 2000.0, "mean": 100.0},
            "temperature_c": {"type": "float64", "min": -50.0, "max": 150.0, "mean": 45.0},
            "vibration_hz": {"type": "float64", "min": 0.0, "max": 150.0, "mean": 10.0},
            "pressure_bar": {"type": "float64", "min": 0.0, "max": 50.0, "mean": 5.0},
            "hour": {"type": "int32", "min": 0.0, "max": 23.0, "mean": 12.0},
            "day_of_week": {"type": "int32", "min": 0.0, "max": 6.0, "mean": 3.0},
            "is_weekend": {"type": "int64", "min": 0.0, "max": 1.0, "mean": 0.28},
            "is_peak_hour": {"type": "int64", "min": 0.0, "max": 1.0, "mean": 0.5},
            "power_kw_lag_1": {"type": "float64", "min": 0.0, "max": 2000.0, "mean": 100.0},
            "power_kw_lag_6": {"type": "float64", "min": 0.0, "max": 2000.0, "mean": 100.0},
            "power_kw_lag_24": {"type": "float64", "min": 0.0, "max": 2000.0, "mean": 100.0},
            "power_rolling_mean": {"type": "float64", "min": 0.0, "max": 2000.0, "mean": 100.0},
            "power_rolling_std": {"type": "float64", "min": 0.0, "max": 500.0, "mean": 15.0},
            "consumption_delta": {"type": "float64", "min": -1000.0, "max": 1000.0, "mean": 0.0},
        },
    }


@pytest.fixture
def feature_validator(sample_schema_v2):
    return FeatureValidator(sample_schema_v2)


@pytest.fixture
def preprocessor():
    return FeaturePreprocessor()


@pytest.fixture
def loaded_manager():
    manager = ModelManager()
    manager.load_models()
    return manager


# =====================================================================
# Tests: FeatureValidator
# =====================================================================

class TestFeatureValidator:
    def test_valid_input_passes(self, feature_validator):
        data = {
            "power_kw": 45.5,
            "temperature_c": 50.0,
            "vibration_hz": 2.5,
            "pressure_bar": 1.8,
            "hour": 14,
        }
        validated = feature_validator.validate_anomaly(data)
        assert validated["power_kw"] == 45.5
        assert validated["temperature_c"] == 50.0
        assert validated["vibration_hz"] == 2.5
        assert validated["pressure_bar"] == 1.8

    def test_missing_essential_feature_raises_error(self, feature_validator):
        data = {"temperature_c": 50.0, "vibration_hz": 2.5}
        with pytest.raises(FeatureValidationError) as exc_info:
            feature_validator.validate_anomaly(data)
        assert "power_kw" in str(exc_info.value)
        assert "missing" in exc_info.value.details

    def test_invalid_type_raises_error(self, feature_validator):
        data = {
            "power_kw": "invalide_non_numerique",
            "temperature_c": 50.0,
            "vibration_hz": 2.5,
            "pressure_bar": 1.8,
        }
        with pytest.raises(FeatureValidationError) as exc_info:
            feature_validator.validate_anomaly(data)
        assert "invalid_types" in exc_info.value.details

    def test_nan_value_is_rejected(self, feature_validator):
        data = {
            "power_kw": float("nan"),
            "temperature_c": 50.0,
            "vibration_hz": 2.5,
            "pressure_bar": 1.8,
        }
        with pytest.raises(FeatureValidationError) as exc_info:
            feature_validator.validate_anomaly(data)
        assert "nan_or_inf" in exc_info.value.details

    def test_infinite_value_is_rejected(self, feature_validator):
        data = {
            "power_kw": float("inf"),
            "temperature_c": 50.0,
            "vibration_hz": 2.5,
            "pressure_bar": 1.8,
        }
        with pytest.raises(FeatureValidationError) as exc_info:
            feature_validator.validate_anomaly(data)
        assert "nan_or_inf" in exc_info.value.details

    def test_strict_bounds_rejection(self, feature_validator):
        data = {
            "power_kw": 5000.0,  # Max est 2000.0 dans le schéma
            "temperature_c": 50.0,
            "vibration_hz": 2.5,
            "pressure_bar": 1.8,
        }
        with pytest.raises(FeatureValidationError) as exc_info:
            feature_validator.validate_anomaly(data, strict_bounds=True)
        assert "out_of_range" in exc_info.value.details

    def test_null_input_raises_error(self, feature_validator):
        with pytest.raises(FeatureValidationError):
            feature_validator.validate(None)


# =====================================================================
# Tests: FeaturePreprocessor
# =====================================================================

class TestFeaturePreprocessor:
    def test_temporal_features_extraction(self):
        dt = datetime(2026, 8, 29, 19, 30, tzinfo=timezone.utc)  # Samedi 19h30
        res = extract_temporal_features(dt)
        assert res["hour"] == 19
        assert res["day_of_week"] == 5  # Samedi
        assert res["is_weekend"] == 1
        assert res["is_peak_hour"] == 1

    def test_forecasting_input_alignment(self, preprocessor):
        raw_data = {"power_kw": 80.0, "temperature_c": 42.0}
        df = preprocessor.prepare_forecasting_input(raw_data)
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == FORECASTING_FEATURES
        assert df["power_kw"].iloc[0] == 80.0
        assert df["temperature_c"].iloc[0] == 42.0
        assert df["power_rolling_mean"].iloc[0] == 80.0  # Imputation cohérente
        assert df["power_rolling_std"].iloc[0] == 0.0

    def test_forecasting_with_history_buffer(self, preprocessor):
        history = [{"power_kw": float(i * 10)} for i in range(1, 30)]
        raw_data = {"power_kw": 300.0, "temperature_c": 40.0}
        df = preprocessor.prepare_forecasting_input(raw_data, history=history)
        assert df["power_kw_lag_1"].iloc[0] == 290.0
        assert df["power_kw_lag_6"].iloc[0] == 240.0
        assert df["power_kw_lag_24"].iloc[0] == 60.0

    def test_anomaly_input_alignment(self, preprocessor):
        raw_data = {
            "power_kw": 120.0,
            "temperature_c": 65.0,
            "vibration_hz": 15.0,
            "pressure_bar": 3.5,
        }
        df = preprocessor.prepare_anomaly_input(raw_data, previous_power=100.0)
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ANOMALY_FEATURES
        assert df["consumption_delta"].iloc[0] == 20.0  # 120 - 100

    def test_data_hash_is_deterministic(self):
        d1 = {"a": 1, "b": 2.5}
        d2 = {"b": 2.5, "a": 1}
        assert compute_data_hash(d1) == compute_data_hash(d2)
        assert len(compute_data_hash(d1)) == 64


# =====================================================================
# Tests: ForecastingService & AnomalyDetectionService
# =====================================================================

class TestServices:
    def test_forecasting_service_predict(self, loaded_manager):
        service = loaded_manager._forecasting_service
        input_data = {
            "power_kw": 50.0,
            "temperature_c": 35.0,
            "hour": 14,
            "day_of_week": 2,
            "is_weekend": 0,
            "is_peak_hour": 1,
        }
        result = service.predict(input_data)
        assert isinstance(result, PredictionResult)
        assert isinstance(result.request_id, str)
        assert len(result.request_id) > 0
        assert result.predicted_value >= 0.0
        assert result.unit == "kW"
        assert result.metadata.execution_time_ms >= 0.0
        assert result.metadata.feature_count == 11

    def test_anomaly_service_detect(self, loaded_manager):
        service = loaded_manager._anomaly_service
        input_data = {
            "power_kw": 45.0,
            "temperature_c": 40.0,
            "vibration_hz": 2.0,
            "pressure_bar": 1.2,
        }
        result = service.detect(input_data)
        assert isinstance(result, AnomalyResult)
        assert isinstance(result.request_id, str)
        assert isinstance(result.is_anomaly, bool)
        assert isinstance(result.score, float)
        assert 0.0 <= result.probability <= 1.0
        assert 0.0 <= result.confidence <= 1.0
        assert result.severity in ("normal", "faible", "modérée", "critique")
        assert result.metadata.execution_time_ms >= 0.0

    def test_unloaded_model_raises_model_not_loaded(self):
        unloaded_forecaster = ForecastingService(model=None)
        with pytest.raises(ModelNotLoadedError):
            unloaded_forecaster.predict({"power_kw": 10.0})

        unloaded_anomaly = AnomalyDetectionService(model=None)
        with pytest.raises(ModelNotLoadedError):
            unloaded_anomaly.detect({"power_kw": 10.0})


# =====================================================================
# Tests: PredictionEngine
# =====================================================================

class TestPredictionEngine:
    def test_end_to_end_forecasting(self, loaded_manager):
        engine = loaded_manager._prediction_engine
        raw_input = {"power_kw": 75.0, "temperature_c": 38.0}
        custom_id = str(uuid.uuid4())
        
        result = engine.predict_forecasting(raw_input, request_id=custom_id)
        assert result.request_id == custom_id
        assert result.predicted_value >= 0.0
        assert result.metadata.execution_time_ms > 0.0

    def test_end_to_end_anomaly_detection(self, loaded_manager):
        engine = loaded_manager._prediction_engine
        raw_input = {
            "power_kw": 95.0,
            "temperature_c": 80.0,
            "vibration_hz": 40.0,
            "pressure_bar": 4.5,
        }
        result = engine.predict_anomaly(raw_input)
        assert isinstance(result.request_id, str)
        assert isinstance(result.is_anomaly, bool)
        assert result.metadata.execution_time_ms > 0.0

    def test_invalid_input_rejected_by_engine(self, loaded_manager):
        engine = loaded_manager._prediction_engine
        with pytest.raises(FeatureValidationError):
            engine.predict_forecasting({"power_kw": "non_convertible"})


# =====================================================================
# Tests: ModelManager Facade
# =====================================================================

class TestModelManager:
    def test_manager_metrics_updated_after_predictions(self, loaded_manager):
        initial_metrics = loaded_manager.get_metrics()
        initial_count = initial_metrics["runtime_inference"]["prediction_count"]

        loaded_manager.predict({"power_kw": 60.0, "temperature_c": 30.0})
        loaded_manager.detect_anomaly({
            "power_kw": 60.0,
            "temperature_c": 30.0,
            "vibration_hz": 1.5,
            "pressure_bar": 1.0,
        })

        updated_metrics = loaded_manager.get_metrics()
        assert updated_metrics["runtime_inference"]["prediction_count"] == initial_count + 2
        assert updated_metrics["runtime_inference"]["avg_execution_time_ms"] >= 0.0

    def test_health_check_healthy(self, loaded_manager):
        health = loaded_manager.health_check()
        assert health.status == "healthy"
        assert health.models_loaded is True
        assert health.registry_loaded is True
        assert health.feature_schema_loaded is True
        assert health.version == "2.0.0"
