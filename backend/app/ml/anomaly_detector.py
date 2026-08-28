"""
app/ml/anomaly_detector.py — Service métier de détection d'anomalies avec Isolation Forest.

Exécute l'inférence du modèle Isolation Forest, évalue la fonction de décision,
calibre les probabilités d'anomalie, mesure la latence et structure la réponse typée.
"""

from datetime import datetime, timezone
import logging
import math
import time
import uuid
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from app.ml.exceptions import ModelNotLoadedError, PredictionError
from app.ml.preprocessing import FeaturePreprocessor, compute_data_hash
from app.ml.types import AnomalyResult, PredictionMetadata

logger = logging.getLogger("nouankany.ml")


class AnomalyDetectionService:
    """
    Service dédié à la détection d'anomalies énergétiques et sensorielles.
    Intègre le prétraitement des données, l'inférence Isolation Forest et la traçabilité.
    """

    def __init__(
        self,
        model: Any = None,
        model_name: str = "IsolationForest_AnomalyDetector",
        version: str = "2.0.0",
        feature_names: Optional[List[str]] = None,
        preprocessor: Optional[FeaturePreprocessor] = None,
    ) -> None:
        """
        Initialise le service de détection d'anomalies.

        :param model: Modèle ou Pipeline Isolation Forest désérialisé.
        :param model_name: Nom identifiant du modèle.
        :param version: Version courante du modèle.
        :param feature_names: Ordre des caractéristiques attendu par le modèle.
        :param preprocessor: Instance optionnelle de `FeaturePreprocessor`.
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
        self.preprocessor = preprocessor or FeaturePreprocessor(
            anomaly_features=self.feature_names
        )

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

    def detect(
        self,
        features: Union[Dict[str, Any], pd.DataFrame],
        previous_power: Optional[float] = None,
        request_id: Optional[str] = None,
    ) -> AnomalyResult:
        """
        Analyse une observation et détermine s'il s'agit d'une anomalie.

        :param features: Dictionnaire ou DataFrame des caractéristiques d'observation.
        :param previous_power: Puissance de l'itération précédente (optionnel).
        :param request_id: Identifiant unique optionnel (un UUID est généré par défaut).
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

        req_id = request_id or str(uuid.uuid4())
        start_time = time.perf_counter()

        try:
            # 1. Prétraitement et alignement strict des caractéristiques
            df_input = self.preprocessor.prepare_anomaly_input(
                features, previous_power=previous_power
            )
            data_hash = compute_data_hash(df_input)

            # 2. Prédiction discrète (-1: anomalie, 1: normal)
            raw_pred = self.model.predict(df_input)
            pred_code = int(raw_pred[0]) if isinstance(raw_pred, (np.ndarray, list, pd.Series)) else int(raw_pred)
            is_anomaly = bool(pred_code == -1)

            # 3. Score de décision brut (decision_function)
            score = 0.0
            if hasattr(self.model, "decision_function"):
                dec = self.model.decision_function(df_input)
                score = float(dec[0])
            elif hasattr(self.model, "named_steps") and hasattr(
                self.model.named_steps.get("model", None), "decision_function"
            ):
                dec = self.model.decision_function(df_input)
                score = float(dec[0])

            # 4. Probabilité calibrée d'anomalie
            # Sigmoïde inversée : score négatif -> probabilité élevée
            prob = 1.0 / (1.0 + math.exp(5.0 * score))
            prob = max(0.0, min(1.0, prob))

            # 5. Confiance de l'inférence (plus on s'éloigne de 0, plus la confiance est forte)
            confidence = min(1.0, max(0.5, 0.5 + abs(score)))

            # 6. Niveau de sévérité métier
            if not is_anomaly:
                severity = "normal"
            elif score < -0.25:
                severity = "critique"
            elif score < -0.10:
                severity = "modérée"
            else:
                severity = "faible"

            execution_time_ms = (time.perf_counter() - start_time) * 1000.0

            metadata = PredictionMetadata(
                request_id=req_id,
                execution_time_ms=round(execution_time_ms, 3),
                timestamp=datetime.now(timezone.utc),
                feature_count=len(self.feature_names),
                data_hash=data_hash,
            )

            result = AnomalyResult(
                request_id=req_id,
                is_anomaly=is_anomaly,
                score=round(score, 4),
                probability=round(prob, 4),
                confidence=round(confidence, 4),
                severity=severity,
                model_name=self.model_name,
                model_version=self.version,
                metadata=metadata,
            )

            logger.info(
                f"[AnomalyDetectionService] [req_id={req_id}] Détection terminée : "
                f"anomalie={is_anomaly} (sévérité={severity}, score={score:.4f}, proba={prob:.4f}, "
                f"latence={execution_time_ms:.2f}ms)"
            )

            return result

        except Exception as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                f"[AnomalyDetectionService] [req_id={req_id}] Échec détection Isolation Forest ({e}) après {execution_time_ms:.2f}ms"
            )
            if isinstance(e, (ModelNotLoadedError, PredictionError)):
                raise
            raise PredictionError(
                f"Échec de l'analyse d'anomalie par Isolation Forest : {e}",
                details={"model_name": self.model_name, "request_id": req_id, "error": str(e)},
            ) from e
