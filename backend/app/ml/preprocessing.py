"""
app/ml/preprocessing.py — Module de prétraitement et alignement des caractéristiques.

Garantit que les transformations appliquées lors de l'inférence sont strictement
identiques à celles de la phase d'entraînement (feature engineering temporel,
calcul des retards/moyennes mobiles, alignement dimensionnel).
"""

from datetime import datetime, timezone
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Sequence, Union
import numpy as np
import pandas as pd

from app.ml.exceptions import PreprocessingError

logger = logging.getLogger("nouankany.ml")

# Caractéristiques attendues par chaque modèle dans leur ordre strict d'entraînement
FORECASTING_FEATURES: List[str] = [
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

ANOMALY_FEATURES: List[str] = [
    "power_kw",
    "temperature_c",
    "vibration_hz",
    "pressure_bar",
    "power_rolling_std",
    "consumption_delta",
    "hour",
]

# Heures de pointe électrique standard en Côte d'Ivoire (18h-23h et pointes diurnes)
PEAK_HOURS: set[int] = {10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22}


def compute_data_hash(data: Union[Dict[str, Any], pd.DataFrame, Sequence[Any]]) -> str:
    """
    Calcule une empreinte SHA-256 déterministe pour la traçabilité des données d'inférence.

    :param data: Dictionnaire ou DataFrame d'entrée.
    :return: Chaîne hexadécimale SHA-256 de 64 caractères.
    """
    try:
        if isinstance(data, pd.DataFrame):
            serialized = data.to_json(orient="split", date_format="iso")
        elif isinstance(data, dict):
            # Tri des clés pour une empreinte déterministe
            serialized = json.dumps(data, sort_keys=True, default=str)
        else:
            serialized = str(data)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    except Exception as e:
        logger.warning(f"[Preprocessing] Impossible de calculer le hash des données: {e}")
        return hashlib.sha256(str(time_now := datetime.now(timezone.utc)).encode("utf-8")).hexdigest()


def extract_temporal_features(
    dt_or_str: Optional[Union[datetime, str]] = None,
) -> Dict[str, int]:
    """
    Extrait les composantes temporelles requises par les modèles à partir d'une date.

    :param dt_or_str: Instance datetime ou chaîne ISO 8601. Si None, utilise l'instant UTC courant.
    :return: Dictionnaire contenant `hour`, `day_of_week`, `is_weekend`, `is_peak_hour`.
    """
    if dt_or_str is None:
        dt = datetime.now(timezone.utc)
    elif isinstance(dt_or_str, str):
        try:
            # Remplacement éventuel du suffixe Z pour compatibilité ISO
            clean_str = dt_or_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_str)
        except Exception:
            dt = datetime.now(timezone.utc)
    elif isinstance(dt_or_str, datetime):
        dt = dt_or_str
    else:
        dt = datetime.now(timezone.utc)

    hour = int(dt.hour)
    day_of_week = int(dt.weekday())  # 0 = Lundi, 6 = Dimanche
    is_weekend = 1 if day_of_week >= 5 else 0
    is_peak_hour = 1 if hour in PEAK_HOURS else 0

    return {
        "hour": hour,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "is_peak_hour": is_peak_hour,
    }


class FeaturePreprocessor:
    """
    Gestionnaire des transformations de prétraitement pour l'inférence.
    Reproduit fidèlement le pipeline de features construit pendant l'entraînement.
    """

    def __init__(
        self,
        forecasting_features: Optional[List[str]] = None,
        anomaly_features: Optional[List[str]] = None,
    ) -> None:
        """
        Initialise le prétraiteur avec les listes de caractéristiques cibles.

        :param forecasting_features: Ordre exact des features pour XGBoost.
        :param anomaly_features: Ordre exact des features pour Isolation Forest.
        """
        self.forecasting_features = forecasting_features or FORECASTING_FEATURES.copy()
        self.anomaly_features = anomaly_features or ANOMALY_FEATURES.copy()
        logger.debug("[FeaturePreprocessor] Initialisé avec les colonnes modèles standard.")

    def prepare_forecasting_input(
        self,
        raw_data: Union[Dict[str, Any], pd.DataFrame],
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> pd.DataFrame:
        """
        Prépare et aligne les caractéristiques pour le modèle de prévision XGBoost.

        Si les caractéristiques temporelles ou de lag/rolling ne sont pas fournies,
        elles sont dérivées automatiquement à partir des lectures disponibles ou de l'historique.

        :param raw_data: Données brutes de capteur ou caractéristiques enrichies.
        :param history: Historique chronologique optionnel pour calcul exact des lags.
        :return: DataFrame pandas 2D ordonné et typé selon `forecasting_features`.
        :raises PreprocessingError: En cas d'impossibilité de prétraiter les données.
        """
        try:
            if isinstance(raw_data, pd.DataFrame):
                data_dict = raw_data.iloc[0].to_dict()
            elif isinstance(raw_data, dict):
                data_dict = raw_data.copy()
            else:
                raise PreprocessingError(
                    f"Type d'entrée non supporté : {type(raw_data)}. Dict ou DataFrame attendu."
                )

            # 1. Extraction de la puissance actuelle de base
            power_kw = float(data_dict.get("power_kw", data_dict.get("power", 0.0)))
            temp_c = float(data_dict.get("temperature_c", data_dict.get("temperature", 25.0)))

            # 2. Dérivation des composantes temporelles si absentes
            temporal = extract_temporal_features(data_dict.get("timestamp") or data_dict.get("recorded_at"))
            hour = int(data_dict.get("hour", temporal["hour"]))
            day_of_week = int(data_dict.get("day_of_week", temporal["day_of_week"]))
            is_weekend = int(data_dict.get("is_weekend", temporal["is_weekend"]))
            is_peak_hour = int(data_dict.get("is_peak_hour", temporal["is_peak_hour"]))

            # 3. Calcul ou imputation des features de retards (lags) et moyennes mobiles
            if history and len(history) > 0:
                # Calcul basé sur l'historique fourni
                powers = [float(h.get("power_kw", power_kw)) for h in history]
                lag_1 = powers[-1] if len(powers) >= 1 else power_kw
                lag_6 = powers[-6] if len(powers) >= 6 else (powers[0] if powers else power_kw)
                lag_24 = powers[-24] if len(powers) >= 24 else (powers[0] if powers else power_kw)
                rolling_window = powers[-6:] if len(powers) >= 6 else powers
                rolling_mean = float(np.mean(rolling_window))
                rolling_std = float(np.std(rolling_window)) if len(rolling_window) > 1 else 0.0
            else:
                # Imputation par défaut cohérente
                lag_1 = float(data_dict.get("power_kw_lag_1", power_kw))
                lag_6 = float(data_dict.get("power_kw_lag_6", power_kw))
                lag_24 = float(data_dict.get("power_kw_lag_24", power_kw))
                rolling_mean = float(data_dict.get("power_rolling_mean", power_kw))
                rolling_std = float(data_dict.get("power_rolling_std", 0.0))

            # 4. Assemblage dans le dictionnaire final avec respect des clés
            processed: Dict[str, Any] = {
                "power_kw": power_kw,
                "power_kw_lag_1": lag_1,
                "power_kw_lag_6": lag_6,
                "power_kw_lag_24": lag_24,
                "power_rolling_mean": rolling_mean,
                "power_rolling_std": rolling_std,
                "hour": hour,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "is_peak_hour": is_peak_hour,
                "temperature_c": temp_c,
            }

            # 5. Construction du DataFrame aligné sur `self.forecasting_features`
            row: Dict[str, List[Any]] = {}
            for col in self.forecasting_features:
                if col in processed:
                    row[col] = [processed[col]]
                elif col in data_dict:
                    row[col] = [data_dict[col]]
                else:
                    row[col] = [0.0]

            df = pd.DataFrame(row)
            return df

        except Exception as e:
            logger.error(f"[FeaturePreprocessor] Échec du prétraitement forecasting : {e}")
            raise PreprocessingError(
                f"Erreur de prétraitement pour la prévision : {e}",
                details={"input": str(raw_data), "error": str(e)},
            ) from e

    def prepare_anomaly_input(
        self,
        raw_data: Union[Dict[str, Any], pd.DataFrame],
        previous_power: Optional[float] = None,
    ) -> pd.DataFrame:
        """
        Prépare et aligne les caractéristiques pour le modèle de détection d'anomalies Isolation Forest.

        :param raw_data: Données brutes de capteurs.
        :param previous_power: Puissance précédente optionnelle pour calculer consumption_delta.
        :return: DataFrame pandas 2D ordonné et typé selon `anomaly_features`.
        :raises PreprocessingError: En cas d'erreur de transformation.
        """
        try:
            if isinstance(raw_data, pd.DataFrame):
                data_dict = raw_data.iloc[0].to_dict()
            elif isinstance(raw_data, dict):
                data_dict = raw_data.copy()
            else:
                raise PreprocessingError(
                    f"Type d'entrée non supporté : {type(raw_data)}. Dict ou DataFrame attendu."
                )

            power_kw = float(data_dict.get("power_kw", data_dict.get("power", 0.0)))
            temp_c = float(data_dict.get("temperature_c", data_dict.get("temperature", 25.0)))
            vibration_hz = float(data_dict.get("vibration_hz", data_dict.get("vibration", 0.0)))
            pressure_bar = float(data_dict.get("pressure_bar", data_dict.get("pressure", 1.0)))

            temporal = extract_temporal_features(data_dict.get("timestamp") or data_dict.get("recorded_at"))
            hour = int(data_dict.get("hour", temporal["hour"]))

            power_rolling_std = float(data_dict.get("power_rolling_std", 0.0))

            # Calcul du delta de consommation
            if "consumption_delta" in data_dict:
                consumption_delta = float(data_dict["consumption_delta"])
            elif previous_power is not None:
                consumption_delta = float(power_kw - previous_power)
            else:
                consumption_delta = 0.0

            processed: Dict[str, Any] = {
                "power_kw": power_kw,
                "temperature_c": temp_c,
                "vibration_hz": vibration_hz,
                "pressure_bar": pressure_bar,
                "power_rolling_std": power_rolling_std,
                "consumption_delta": consumption_delta,
                "hour": hour,
            }

            row: Dict[str, List[Any]] = {}
            for col in self.anomaly_features:
                if col in processed:
                    row[col] = [processed[col]]
                elif col in data_dict:
                    row[col] = [data_dict[col]]
                else:
                    row[col] = [0.0]

            df = pd.DataFrame(row)
            return df

        except Exception as e:
            logger.error(f"[FeaturePreprocessor] Échec du prétraitement anomalie : {e}")
            raise PreprocessingError(
                f"Erreur de prétraitement pour la détection d'anomalie : {e}",
                details={"input": str(raw_data), "error": str(e)},
            ) from e
