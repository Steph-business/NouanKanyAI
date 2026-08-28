"""
app/ml/validators.py — Valideur de caractéristiques d'entrée pour les modèles ML.

Vérifie l'intégrité, la complétude, les types et les plages de valeurs des données
d'entrée à l'aide du schéma de caractéristiques (`feature_schema.json`).
"""

import logging
import math
from typing import Any, Dict, List, Optional, Sequence, Union
import numpy as np
import pandas as pd

from app.ml.exceptions import FeatureValidationError

logger = logging.getLogger("nouankany.ml")


class FeatureValidator:
    """
    Composant de validation des données d'entrée par rapport au schéma des caractéristiques.
    Vérifie la présence des colonnes requises, les types, les plages de valeurs (min/max),
    l'absence de valeurs manquantes (None, NaN, Inf) et propose des méthodes dédiées par modèle.
    """

    def __init__(self, feature_schema: Dict[str, Any]) -> None:
        """
        Initialise le valideur avec un schéma de caractéristiques.

        :param feature_schema: Dictionnaire décrivant le schéma (v1 ou v2).
        """
        self.schema = feature_schema
        self._parsed_schema = self._parse_schema(feature_schema)
        self._forecasting_required: List[str] = self._extract_model_features("forecasting")
        self._anomaly_required: List[str] = self._extract_model_features("anomaly_detection")

        logger.debug(
            f"[FeatureValidator] Initialisé avec {len(self._parsed_schema)} spécification(s) de caractéristiques."
        )

    def _parse_schema(self, schema: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Normalise les schémas v1 et v2 dans une structure uniforme de règles par feature.

        :param schema: Dictionnaire du schéma brut.
        :return: Dictionnaire des règles par caractéristique {nom_feature: {type, min, max, mean}}.
        """
        parsed: Dict[str, Dict[str, Any]] = {}

        # Format v2 avec clé 'features' contenant des dictionnaires d'attributs
        if "features" in schema and isinstance(schema["features"], dict):
            for name, rules in schema["features"].items():
                if isinstance(rules, dict):
                    parsed[name] = {
                        "type": rules.get("type", "float64"),
                        "min": rules.get("min"),
                        "max": rules.get("max"),
                        "mean": rules.get("mean"),
                    }
                else:
                    parsed[name] = {"type": "float64", "min": None, "max": None, "mean": None}

        # Format v1 avec 'forecasting' et 'anomaly_detection' contenant des listes de noms
        else:
            all_features: List[str] = []
            if "forecasting" in schema and isinstance(schema["forecasting"], dict):
                all_features.extend(schema["forecasting"].get("features", []))
            if "anomaly_detection" in schema and isinstance(schema["anomaly_detection"], dict):
                all_features.extend(schema["anomaly_detection"].get("features", []))

            for feat in set(all_features):
                parsed[feat] = {"type": "float64", "min": None, "max": None, "mean": None}

        return parsed

    def _extract_model_features(self, target: str) -> List[str]:
        """
        Extrait la liste ordonnée des caractéristiques requises pour un modèle donné.

        :param target: 'forecasting' ou 'anomaly_detection'.
        :return: Liste de noms de caractéristiques.
        """
        if target in self.schema and isinstance(self.schema[target], dict):
            return list(self.schema[target].get("features", []))
        
        if target == "forecasting":
            return [
                "power_kw", "power_kw_lag_1", "power_kw_lag_6", "power_kw_lag_24",
                "power_rolling_mean", "power_rolling_std", "hour", "day_of_week",
                "is_weekend", "is_peak_hour", "temperature_c"
            ]
        elif target == "anomaly_detection":
            return [
                "power_kw", "temperature_c", "vibration_hz", "pressure_bar",
                "power_rolling_std", "consumption_delta", "hour"
            ]
        return list(self._parsed_schema.keys())

    def get_expected_features(self, target: str = "forecasting") -> List[str]:
        """
        Retourne la liste des caractéristiques attendues pour une cible.

        :param target: 'forecasting', 'anomaly_detection' ou 'all'.
        :return: Liste des noms de caractéristiques.
        """
        if target == "forecasting":
            return self._forecasting_required.copy()
        elif target in ("anomaly", "anomaly_detection"):
            return self._anomaly_required.copy()
        return list(self._parsed_schema.keys())

    def get_feature_rules(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """
        Retourne les règles associées à une caractéristique spécifique.

        :param feature_name: Nom de la variable.
        :return: Dictionnaire de règles (type, min, max) ou None si non répertoriée.
        """
        return self._parsed_schema.get(feature_name)

    def validate(
        self,
        data: Union[Dict[str, Any], pd.DataFrame, pd.Series],
        required_features: Optional[Sequence[str]] = None,
        allow_extra: bool = True,
        strict_bounds: bool = False,
    ) -> Dict[str, Any]:
        """
        Valide un dictionnaire ou une observation de caractéristiques.

        :param data: Dictionnaire clé-valeur d'entrée ou Series pandas.
        :param required_features: Liste des caractéristiques strictement requises.
        :param allow_extra: Si True, conserve les clés supplémentaires sans lever d'erreur.
        :param strict_bounds: Si True, rejette strictement les valeurs hors bornes [min, max].
        :return: Le dictionnaire validé et typé numériquement.
        :raises FeatureValidationError: Si les données sont invalides (manquantes, types, bornes, NaN/Inf).
        """
        if data is None:
            raise FeatureValidationError(
                "Les données d'entrée sont nulles (None). Un dictionnaire de caractéristiques est requis.",
                details={"error_code": "NULL_INPUT"},
            )

        if isinstance(data, pd.DataFrame):
            if data.empty:
                raise FeatureValidationError(
                    "Le DataFrame fourni est vide.", details={"error_code": "EMPTY_DATAFRAME"}
                )
            input_dict = data.iloc[0].to_dict()
        elif isinstance(data, pd.Series):
            input_dict = data.to_dict()
        elif isinstance(data, dict):
            input_dict = data.copy()
        else:
            raise FeatureValidationError(
                f"Type d'entrée invalide : {type(data)}. Dictionnaire ou DataFrame attendu.",
                details={"received_type": str(type(data)), "error_code": "INVALID_TYPE"},
            )

        features_to_check = list(required_features) if required_features is not None else list(self._parsed_schema.keys())

        missing_features: List[str] = []
        invalid_types: List[str] = []
        out_of_range: List[str] = []
        nan_or_inf_features: List[str] = []
        validated_data: Dict[str, Any] = {}

        # 1. Validation des caractéristiques requises
        for feat in features_to_check:
            if feat not in input_dict or input_dict[feat] is None:
                missing_features.append(feat)
                continue

            raw_val = input_dict[feat]

            # Vérification de convertibilité numérique
            try:
                numeric_val = float(raw_val)
            except (ValueError, TypeError):
                invalid_types.append(
                    f"'{feat}': valeur '{raw_val}' non convertible en nombre réel."
                )
                continue

            # Vérification NaN / Infinis
            if math.isnan(numeric_val) or math.isinf(numeric_val):
                nan_or_inf_features.append(
                    f"'{feat}': valeur invalide détectée (NaN ou Infini)."
                )
                continue

            # Conversion entière si le schéma le spécifie
            rule = self._parsed_schema.get(feat, {})
            expected_type = rule.get("type", "float64")
            if "int" in expected_type:
                validated_data[feat] = int(round(numeric_val))
            else:
                validated_data[feat] = numeric_val

            # Vérification des bornes
            min_val = rule.get("min")
            max_val = rule.get("max")

            # Exclusion des sentinelles extrêmes comme -999.0 / 999.0
            is_min_sentinel = min_val is not None and abs(abs(min_val) - 999.0) < 1e-3
            is_max_sentinel = max_val is not None and abs(abs(max_val) - 999.0) < 1e-3

            if min_val is not None and not is_min_sentinel:
                if numeric_val < min_val:
                    msg = f"'{feat}': {numeric_val} < borne minimale {min_val}"
                    if strict_bounds:
                        out_of_range.append(msg)
                    else:
                        logger.debug(f"[FeatureValidator] Avertissement plage: {msg}")

            if max_val is not None and not is_max_sentinel:
                if numeric_val > max_val:
                    msg = f"'{feat}': {numeric_val} > borne maximale {max_val}"
                    if strict_bounds:
                        out_of_range.append(msg)
                    else:
                        logger.debug(f"[FeatureValidator] Avertissement plage: {msg}")

        # 2. Conservation des attributs complémentaires utiles si autorisés
        if allow_extra:
            for k, v in input_dict.items():
                if k not in validated_data:
                    validated_data[k] = v

        # 3. Consolidation et rapport des erreurs
        errors: List[str] = []
        if missing_features:
            errors.append(
                f"Caractéristiques requises manquantes : {', '.join(missing_features)}"
            )
        if invalid_types:
            errors.append(
                f"Incompatibilité de type détectée : {'; '.join(invalid_types)}"
            )
        if nan_or_inf_features:
            errors.append(
                f"Valeurs NaN/Infinies rejetées : {'; '.join(nan_or_inf_features)}"
            )
        if out_of_range:
            errors.append(
                f"Valeurs hors limites strictes : {'; '.join(out_of_range)}"
            )

        if errors:
            error_msg = "Échec de validation des caractéristiques d'entrée."
            logger.error(f"[FeatureValidator] {error_msg} | {errors}")
            raise FeatureValidationError(
                error_msg,
                details={
                    "missing": missing_features,
                    "invalid_types": invalid_types,
                    "nan_or_inf": nan_or_inf_features,
                    "out_of_range": out_of_range,
                    "all_errors": errors,
                },
            )

        return validated_data

    def validate_forecasting(
        self, data: Union[Dict[str, Any], pd.DataFrame], strict_bounds: bool = False
    ) -> Dict[str, Any]:
        """
        Valide spécifiquement les données pour le modèle de prévision (XGBoost).

        :param data: Dictionnaire de données.
        :param strict_bounds: Si True, applique strictement les bornes min/max.
        :return: Dictionnaire validé.
        """
        # Au minimum, 'power_kw' et 'temperature_c' sont indispensables
        # Les autres peuvent être dérivées par le FeaturePreprocessor si nécessaire
        essential = ["power_kw"]
        return self.validate(
            data=data,
            required_features=essential,
            allow_extra=True,
            strict_bounds=strict_bounds,
        )

    def validate_anomaly(
        self, data: Union[Dict[str, Any], pd.DataFrame], strict_bounds: bool = False
    ) -> Dict[str, Any]:
        """
        Valide spécifiquement les données pour la détection d'anomalies (Isolation Forest).

        :param data: Dictionnaire de données.
        :param strict_bounds: Si True, applique strictement les bornes min/max.
        :return: Dictionnaire validé.
        """
        essential = ["power_kw", "temperature_c", "vibration_hz", "pressure_bar"]
        return self.validate(
            data=data,
            required_features=essential,
            allow_extra=True,
            strict_bounds=strict_bounds,
        )
