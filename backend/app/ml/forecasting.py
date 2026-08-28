"""
app/ml/forecasting.py — Service métier de prévision énergétique avec le modèle XGBoost.
"""

from datetime import datetime, timezone
import logging
import time
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from app.ml.exceptions import ModelNotLoadedError, PredictionError
from app.ml.types import PredictionMetadata, PredictionResult

logger = logging.getLogger("nouankany.ml")


class ForecastingService:
    """
    Service dédié à la prévision de la consommation énergétique à t+1 heure.
    Utilise exclusivement le modèle XGBoost (ou son Pipeline scikit-learn).
    """

    def __init__(
        self,
        model: Any = None,
        model_name: str = "XGBoost_Forecaster",
        version: str = "2.0.0",
        feature_names: Optional[List[str]] = None,
    ) -> None:
        """
        Initialise le service de prévision.

        :param model: Objet modèle désérialisé (sklearn Pipeline ou XGBRegressor).
        :param model_name: Nom identifiant le modèle.
        :param version: Version du modèle.
        :param feature_names: Ordre des caractéristiques attendu par le modèle.
        """
        self.model = model
        self.model_name = model_name
        self.version = version
        self.feature_names = feature_names or [
            "power_kw",
            "power_kw_lag_1",
            "power_kw_lag_6",
            "power_kw_lag_24",
            "power_rolling_mean",
            "power_rolling_std",
            "hour",
            "day_of_week",
            "is_weekend",
            "is_peak_hour",
            "temperature_c",
        ]
        logger.debug(
            f"[ForecastingService] Initialisé (model_name={model_name}, version={version}, features_count={len(self.feature_names)})"
        )

    def set_model(self, model: Any, version: str = "2.0.0") -> None:
        """
        Injecte ou met à jour le modèle XGBoost.

        :param model: Instance désérialisée du modèle.
        :param version: Nouvelle version associées.
        """
        self.model = model
        self.version = version
        logger.info(f"[ForecastingService] Modèle mis à jour (version {version}).")

    def predict(self, validated_features: Dict[str, Any]) -> PredictionResult:
        """
        Effectue la prédiction de consommation énergétique t+1.

        :param validated_features: Dictionnaire des caractéristiques pré-validées.
        :return: Instance typée `PredictionResult`.
        :raises ModelNotLoadedError: Si le modèle XGBoost n'a pas été chargé.
        :raises PredictionError: Si le calcul d'inférence échoue.
        """
        if self.model is None:
            logger.error("[ForecastingService] Tentative de prédiction sur modèle non chargé.")
            raise ModelNotLoadedError(
                "Le modèle de prévision XGBoost n'est pas chargé en mémoire.",
                details={"model_name": self.model_name},
            )

        start_time = time.perf_counter()

        try:
            # Préparation du DataFrame avec le bon ordre de colonnes
            row_data = {}
            for col in self.feature_names:
                row_data[col] = [validated_features.get(col, 0.0)]
            
            df_input = pd.DataFrame(row_data)

            # Execution de predict
            raw_pred = self.model.predict(df_input)
            
            # Traitement de la sortie (float)
            if isinstance(raw_pred, (np.ndarray, list)):
                predicted_val = float(raw_pred[0])
            else:
                predicted_val = float(raw_pred)

            execution_time_ms = (time.perf_counter() - start_time) * 1000.0

            metadata = PredictionMetadata(
                execution_time_ms=round(execution_time_ms, 3),
                timestamp=datetime.now(timezone.utc),
                feature_count=len(self.feature_names),
                data_hash=None,
            )

            logger.info(
                f"[ForecastingService] Prédiction réussie : {predicted_val:.2f} kW en {execution_time_ms:.2f}ms"
            )

            return PredictionResult(
                predicted_value=round(predicted_val, 4),
                unit="kW",
                model_name=self.model_name,
                model_version=self.version,
                metadata=metadata,
            )

        except Exception as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                f"[ForecastingService] Échec de prédiction XGBoost ({e}) après {execution_time_ms:.2f}ms"
            )
            raise PredictionError(
                f"Échec de prédiction par le modèle de prévision XGBoost : {e}",
                details={"model_name": self.model_name, "error": str(e)},
            ) from e
