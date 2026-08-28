"""
app/ml/anomaly_detector.py — Service métier de détection d'anomalies avec Isolation Forest.
"""

from datetime import datetime, timezone
import logging
import math
import time
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from app.ml.exceptions import ModelNotLoadedError, PredictionError
from app.ml.types import AnomalyResult, PredictionMetadata

logger = logging.getLogger("nouankany.ml")


class AnomalyDetectionService:
    """
    Service dédié à la détection d'anomalies énergétiques et sensorielles.
    Utilise exclusivement le modèle Isolation Forest (ou son Pipeline scikit-learn).
    """

    def __init__(
        self,
        model: Any = None,
        model_name: str = "IsolationForest_AnomalyDetector",
        version: str = "2.0.0",
        feature_names: Optional[List[str]] = None,
    ) -> None:
        """
        Initialise le service de détection d'anomalies.

        :param model: Modèle ou Pipeline Isolation Forest désérialisé.
        :param model_name: Nom identifiant du modèle.
        :param version: Version courante du modèle.
        :param feature_names: Ordre des caractéristiques attendu par le modèle.
        """
        self.model = model
        self.model_name = model_name
        self.version = version
        self.feature_names = feature_names or [
            "power_kw",
            "temperature_c",
            "vibration_hz",
            "pressure_bar",
            "power_rolling_std",
            "consumption_delta",
            "hour",
        ]
        logger.debug(
            f"[AnomalyDetectionService] Initialisé (model_name={model_name}, version={version})"
        )

    def set_model(self, model: Any, version: str = "2.0.0") -> None:
        """
        Injecte ou met à jour le modèle Isolation Forest.

        :param model: Modèle désérialisé.
        :param version: Version associée.
        """
        self.model = model
        self.version = version
        logger.info(
            f"[AnomalyDetectionService] Modèle mis à jour (version {version})."
        )

    def detect(self, validated_features: Dict[str, Any]) -> AnomalyResult:
        """
        Analyse une observation et détermine s'il s'agit d'une anomalie.

        :param validated_features: Dictionnaire des caractéristiques validées.
        :return: Instance typée `AnomalyResult`.
        :raises ModelNotLoadedError: Si le modèle Isolation Forest n'est pas chargé.
        :raises PredictionError: Si le calcul de détection échoue.
        """
        if self.model is None:
            logger.error(
                "[AnomalyDetectionService] Tentative de détection sur modèle non chargé."
            )
            raise ModelNotLoadedError(
                "Le modèle Isolation Forest n'est pas chargé en mémoire.",
                details={"model_name": self.model_name},
            )

        start_time = time.perf_counter()

        try:
            # Préparation du DataFrame avec le bon ordre de colonnes
            row_data = {}
            for col in self.feature_names:
                row_data[col] = [validated_features.get(col, 0.0)]

            df_input = pd.DataFrame(row_data)

            # 1. Prediction directe (-1 pour anomalie, 1 pour normal)
            raw_pred = self.model.predict(df_input)
            pred_code = int(raw_pred[0]) if isinstance(raw_pred, (np.ndarray, list)) else int(raw_pred)
            is_anomaly = pred_code == -1

            # 2. Decision function (score de décision brut)
            score = 0.0
            if hasattr(self.model, "decision_function"):
                dec = self.model.decision_function(df_input)
                score = float(dec[0])
            elif hasattr(self.model, "named_steps") and hasattr(
                self.model.named_steps.get("model", None), "decision_function"
            ):
                # Cas d'un Pipeline sklearn
                dec = self.model.decision_function(df_input)
                score = float(dec[0])

            # 3. Calcul de la probabilité d'anomalie
            # Dans Isolation Forest decision_function : score négatif = anomalie, score positif = normal.
            # Sigmoïde inversée : P(anomalie) = 1 / (1 + exp(k * score))
            prob = 1.0 / (1.0 + math.exp(5.0 * score))
            prob = max(0.0, min(1.0, prob))

            # 4. Calcul de la confiance
            # Plus le score est éloigné de 0 (le seuil de décision), plus la confiance est élevée.
            confidence = min(1.0, 0.5 + abs(score))

            execution_time_ms = (time.perf_counter() - start_time) * 1000.0

            metadata = PredictionMetadata(
                execution_time_ms=round(execution_time_ms, 3),
                timestamp=datetime.now(timezone.utc),
                feature_count=len(self.feature_names),
                data_hash=None,
            )

            logger.info(
                f"[AnomalyDetectionService] Détection terminée : anomalie={is_anomaly}, score={score:.4f}, proba={prob:.4f} en {execution_time_ms:.2f}ms"
            )

            return AnomalyResult(
                is_anomaly=is_anomaly,
                score=round(score, 4),
                probability=round(prob, 4),
                confidence=round(confidence, 4),
                model_name=self.model_name,
                model_version=self.version,
                metadata=metadata,
            )

        except Exception as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                f"[AnomalyDetectionService] Échec détection Isolation Forest ({e}) après {execution_time_ms:.2f}ms"
            )
            raise PredictionError(
                f"Échec de l'analyse d'anomalie par Isolation Forest : {e}",
                details={"model_name": self.model_name, "error": str(e)},
            ) from e
