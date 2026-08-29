"""
backend/tests/ml/test_validator.py — Tests unitaires pour FeatureValidator.

Vérifie la validation stricte des features d'entrée contre feature_schema.json,
la détection des valeurs manquantes, des types invalides, des NaN et des infinis.
"""

import pytest
import math
from app.ml.validators import FeatureValidator
from app.ml.exceptions import FeatureValidationError
from app.ml.loader import ModelLoader


class TestFeatureValidator:
    """Suite de tests unitaires pour le validateur de caractéristiques FeatureValidator."""

    @pytest.fixture(autouse=True)
    def setup_validator(self):
        loader = ModelLoader()
        schema = loader.load_feature_schema()
        self.validator = FeatureValidator(feature_schema=schema)

    def test_valid_forecasting_features(self):
        """Vérifie l'acceptation d'un ensemble de features nominales pour la prévision."""
        valid_input = {
            "power_kw": 15.0,
            "power_kw_lag_1": 15.0,
            "power_kw_lag_6": 14.5,
            "power_kw_lag_24": 15.2,
            "power_rolling_mean": 14.8,
            "power_rolling_std": 0.5,
            "hour": 14,
            "day_of_week": 2,
            "is_weekend": 0,
            "is_peak_hour": 1,
            "temperature_c": 26.5,
        }
        validated = self.validator.validate_forecasting(valid_input)
        assert isinstance(validated, dict)
        assert validated["temperature_c"] == 26.5

    def test_valid_anomaly_features(self):
        """Vérifie l'acceptation d'un ensemble de features nominales pour la détection d'anomalie."""
        valid_input = {
            "power_kw": 18.5,
            "temperature_c": 32.0,
            "vibration_hz": 15.0,
            "pressure_bar": 2.2,
            "power_rolling_std": 0.5,
            "consumption_delta": 0.3,
            "hour": 10,
        }
        validated = self.validator.validate_anomaly(valid_input)
        assert isinstance(validated, dict)
        assert validated["power_kw"] == 18.5

    def test_nan_and_inf_values_raise_validation_error(self):
        """Vérifie le rejet des valeurs flottantes spéciales NaN et Infinity."""
        nan_input = {
            "power_kw": float("nan"),
            "power_kw_lag_1": 15.0,
            "power_kw_lag_6": 14.5,
            "power_kw_lag_24": 15.2,
            "power_rolling_mean": 14.8,
            "power_rolling_std": 0.5,
            "hour": 14,
            "day_of_week": 2,
            "is_weekend": 0,
            "is_peak_hour": 1,
            "temperature_c": 26.5,
        }
        with pytest.raises(FeatureValidationError):
            self.validator.validate_forecasting(nan_input)

        inf_input = {
            "power_kw": float("inf"),
            "power_kw_lag_1": 15.0,
            "power_kw_lag_6": 14.5,
            "power_kw_lag_24": 15.2,
            "power_rolling_mean": 14.8,
            "power_rolling_std": 0.5,
            "hour": 14,
            "day_of_week": 2,
            "is_weekend": 0,
            "is_peak_hour": 1,
            "temperature_c": 26.5,
        }
        with pytest.raises(FeatureValidationError):
            self.validator.validate_forecasting(inf_input)

    def test_invalid_type_conversion_raises_error(self):
        """Vérifie le rejet des types non convertibles en float/int."""
        invalid_type_input = {
            "power_kw": "texte_non_numerique",
            "power_kw_lag_1": 15.0,
            "power_kw_lag_6": 14.5,
            "power_kw_lag_24": 15.2,
            "power_rolling_mean": 14.8,
            "power_rolling_std": 0.5,
            "hour": 14,
            "day_of_week": 2,
            "is_weekend": 0,
            "is_peak_hour": 1,
            "temperature_c": 26.5,
        }
        with pytest.raises(FeatureValidationError):
            self.validator.validate_forecasting(invalid_type_input)

    def test_null_input_raises_error(self):
        """Vérifie qu'une entrée None provoque une FeatureValidationError."""
        with pytest.raises(FeatureValidationError):
            self.validator.validate(None)
