"""
app/ml/validators.py — Valideur de caractéristiques d'entrée pour les modèles ML.
"""

import logging
from typing import Any, Dict, List, Optional

from app.ml.exceptions import FeatureValidationError

logger = logging.getLogger("nouankany.ml")


class FeatureValidator:
    """
    Composant de validation des données d'entrée par rapport au schéma des caractéristiques.
    Vérifie la présence des colonnes requises, les types, les plages de valeurs (min/max)
    et l'absence de valeurs manquantes (None / NaN).
    """

    def __init__(self, feature_schema: Dict[str, Any]) -> None:
        """
        Initialise le valideur avec un schéma de caractéristiques.

        :param feature_schema: Dictionnaire décrivant le schéma (v1 ou v2).
        """
        self.schema = feature_schema
        self._parsed_schema = self._parse_schema(feature_schema)
        logger.debug(
            f"[FeatureValidator] Initialisé avec {len(self._parsed_schema)} spécification(s) de caractéristiques."
        )

    def _parse_schema(self, schema: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Normalise les schémas v1 et v2 dans une structure uniforme.

        :param schema: Dictionnaire du schéma brut.
        :return: Dictionnaire des règles par caractéristique.
        """
        parsed: Dict[str, Dict[str, Any]] = {}

        # Format v2 avec clé 'features' contenant des dictionnaires d'attributs
        if "features" in schema and isinstance(schema["features"], dict):
            for name, rules in schema["features"].items():
                parsed[name] = {
                    "type": rules.get("type", "float64"),
                    "min": rules.get("min"),
                    "max": rules.get("max"),
                }
        # Format v1 avec 'forecasting' et 'anomaly_detection' contenant des listes de noms
        else:
            all_features: List[str] = []
            if "forecasting" in schema and "features" in schema["forecasting"]:
                all_features.extend(schema["forecasting"]["features"])
            if "anomaly_detection" in schema and "features" in schema["anomaly_detection"]:
                all_features.extend(schema["anomaly_detection"]["features"])
            
            for feat in set(all_features):
                parsed[feat] = {"type": "float64", "min": None, "max": None}

        return parsed

    def validate(
        self, data: Dict[str, Any], required_features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Valide un dictionnaire de caractéristiques transmises.

        :param data: Dictionnaire clé-valeur d'entrée.
        :param required_features: Liste optionnelle des caractéristiques strictement requises.
        :return: Le dictionnaire validé et éventuellement transtypé.
        :raises FeatureValidationError: Si une caractéristique est manquante, hors limite ou de type incompatible.
        """
        if not isinstance(data, dict):
            logger.error(
                f"[FeatureValidator] Format d'entrée invalide (type attendu: dict, reçu: {type(data)})"
            )
            raise FeatureValidationError(
                "Les données d'entrée doivent être fournies sous forme de dictionnaire clé-valeur.",
                details={"received_type": str(type(data))},
            )

        features_to_check = required_features or list(self._parsed_schema.keys())
        missing_features: List[str] = []
        invalid_types: List[str] = []
        out_of_range: List[str] = []
        validated_data: Dict[str, Any] = {}

        for feat in features_to_check:
            # 1. Vérification de présence
            if feat not in data or data[feat] is None:
                missing_features.append(feat)
                continue

            val = data[feat]

            # 2. Conversion et vérification de type numérique
            try:
                numeric_val = float(val)
                validated_data[feat] = numeric_val
            except (ValueError, TypeError):
                invalid_types.append(
                    f"'{feat}': valeur '{val}' non convertible en nombre."
                )
                continue

            # 3. Vérification des plages min/max (si définies dans le schéma)
            if feat in self._parsed_schema:
                rule = self._parsed_schema[feat]
                min_val = rule.get("min")
                max_val = rule.get("max")

                # Ignorer les valeurs extrêmes sentinelles comme -999 / 999 du schéma
                if min_val is not None and abs(min_val) < 900.0 and numeric_val < min_val:
                    out_of_range.append(
                        f"'{feat}': {numeric_val} < valeur minimale autorisée {min_val}"
                    )
                if max_val is not None and abs(max_val) < 900.0 and numeric_val > max_val:
                    out_of_range.append(
                        f"'{feat}': {numeric_val} > valeur maximale autorisée {max_val}"
                    )

        # Rapport des erreurs
        errors: List[str] = []
        if missing_features:
            errors.append(
                f"Caractéristiques requises manquantes : {', '.join(missing_features)}"
            )
        if invalid_types:
            errors.append(
                f"Incompatibilité de type détectée : {'; '.join(invalid_types)}"
            )
        if out_of_range:
            errors.append(
                f"Valeurs hors de la plage définie : {'; '.join(out_of_range)}"
            )

        if errors:
            error_message = "Échec de validation des caractéristiques d'entrée."
            logger.error(
                f"[FeatureValidator] {error_message} | Erreurs : {errors}"
            )
            raise FeatureValidationError(
                error_message,
                details={
                    "missing": missing_features,
                    "invalid_types": invalid_types,
                    "out_of_range": out_of_range,
                    "all_errors": errors,
                },
            )

        logger.info(
            f"[FeatureValidator] Validation réussie pour {len(validated_data)} caractéristique(s)."
        )
        return validated_data
