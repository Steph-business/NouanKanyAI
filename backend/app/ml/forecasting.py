"""
app/ml/forecasting.py — Service métier de prévision énergétique avec le modèle XGBoost.

Exécute l'inférence du modèle XGBoost, mesure automatiquement la latence,
génère un identifiant unique (UUID) et structure la réponse typée.
"""

from datetime import datetime, timezone
import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from app.ml.exceptions import ModelNotLoadedError, PredictionError
from app.ml.preprocessing import FeaturePreprocessor, compute_data_hash
from app.ml.types import PredictionMetadata, PredictionResult

logger = logging.getLogger("nouankany.ml")


class ForecastingService:
    """
    Service dédié à la prévision de la consommation énergétique à t+1 heure.
    Intègre le prétraitement des données, l'inférence XGBoost et la traçabilité.
    """

    def __init__(
        self,
        model: Any = None,
        model_name: str = "XGBoost_Forecaster",
        version: str = "2.0.0",
        feature_names: Optional[List[str]] = None,
        preprocessor: Optional[FeaturePreprocessor] = None,
    ) -> None:
        """
        Initialise le service de prévision.

        :param model: Objet modèle désérialisé (Pipeline sklearn ou XGBRegressor).
        :param model_name: Nom identifiant le modèle.
        :param version: Version du modèle.
        :param feature_names: Ordre des caractéristiques attendu par le modèle.
        :param preprocessor: Instance optionnelle de `FeaturePreprocessor`.
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
        self.preprocessor = preprocessor or FeaturePreprocessor(
            forecasting_features=self.feature_names
        )

        logger.debug(
            f"[ForecastingService] Initialisé (model_name={model_name}, version={version}, features_count={len(self.feature_names)})"
        )

    def set_model(self, model: Any, version: str = "2.0.0") -> None:
        """
        Injecte ou met à jour le modèle XGBoost.

        :param model: Instance désérialisée du modèle.
        :param version: Nouvelle version associée.
        """
        self.model = model
        self.version = version
        logger.info(f"[ForecastingService] Modèle mis à jour (version {version}).")

    def predict(
        self,
        features: Union[Dict[str, Any], pd.DataFrame],
        history: Optional[List[Dict[str, Any]]] = None,
        request_id: Optional[str] = None,
    ) -> PredictionResult:
        """
        Effectue la prédiction de consommation énergétique t+1.

        :param features: Dictionnaire ou DataFrame des caractéristiques.
        :param history: Historique chronologique optionnel pour calcul exact des retards/moyennes mobiles.
        :param request_id: Identifiant unique optionnel (un UUID est généré par défaut).
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

        req_id = request_id or str(uuid.uuid4())
        start_time = time.perf_counter()

        try:
            # 1. Prétraitement et alignement strict des caractéristiques
            df_input = self.preprocessor.prepare_forecasting_input(features, history=history)
            data_hash = compute_data_hash(df_input)

            # 2. Exécution de l'inférence
            raw_pred = self.model.predict(df_input)

            # 3. Extraction de la valeur scalaire
            if isinstance(raw_pred, (np.ndarray, list, pd.Series)):
                predicted_val = float(raw_pred[0])
            else:
                predicted_val = float(raw_pred)

            # La consommation électrique ne peut être négative
            predicted_val = max(0.0, predicted_val)

            execution_time_ms = (time.perf_counter() - start_time) * 1000.0

            metadata = PredictionMetadata(
                request_id=req_id,
                execution_time_ms=round(execution_time_ms, 3),
                timestamp=datetime.now(timezone.utc),
                feature_count=len(self.feature_names),
                data_hash=data_hash,
            )

            result = PredictionResult(
                request_id=req_id,
                predicted_value=round(predicted_val, 4),
                unit="kW",
                model_name=self.model_name,
                model_version=self.version,
                metadata=metadata,
            )

            logger.info(
                f"[ForecastingService] [req_id={req_id}] Prédiction réussie : {predicted_val:.2f} kW "
                f"(latence: {execution_time_ms:.2f}ms, modèle: {self.model_name} v{self.version})"
            )

            return result

        except Exception as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                f"[ForecastingService] [req_id={req_id}] Échec de prédiction XGBoost ({e}) après {execution_time_ms:.2f}ms"
            )
            if isinstance(e, (ModelNotLoadedError, PredictionError)):
                raise
            raise PredictionError(
                f"Échec de prédiction par le modèle de prévision XGBoost : {e}",
                details={"model_name": self.model_name, "request_id": req_id, "error": str(e)},
            ) from e
