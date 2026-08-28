"""
app/api/v1/ml/router.py — Routes REST versionnées pour l'API Machine Learning de NouanKanyAI.

Expose les capacités de prévision énergétique, détection d'anomalies, diagnostic de santé,
registre de modèles, observabilité et rechargement à chaud.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import get_model_manager, verify_ml_admin_key
from app.ml.manager import ModelManager
from app.ml.types import HealthStatus, ModelInfo
from app.schemas.ml import (
    AnomalyDetectionRequest,
    AnomalyResponseSchema,
    ForecastingRequest,
    PredictionMetadataSchema,
    PredictionResponseSchema,
    ReloadResponseSchema,
    StandardErrorResponse,
)

logger = logging.getLogger("nouankany.ml")

router = APIRouter(
    prefix="",
    tags=["Machine Learning"],
    responses={
        422: {"model": StandardErrorResponse, "description": "Erreur de validation des données d'entrée"},
        500: {"model": StandardErrorResponse, "description": "Erreur interne du sous-système ML"},
        503: {"model": StandardErrorResponse, "description": "Sous-système ou modèle non disponible"},
    },
)


# =====================================================================
# 1. Endpoint : Prévision Énergétique (XGBoost)
# =====================================================================

@router.post(
    "/predict",
    response_model=PredictionResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Prévision de la consommation énergétique à t+1 heure",
    description="""
    Exécute le pipeline de prévision **XGBoost (v2.0.0)**.
    
    - **Entrées acceptées** :
      - Caractéristiques brutes de capteurs (`power_kw`, `temperature_c`).
      - Ou ensemble complet des variables temporelles et retards (`power_kw_lag_1`, `power_rolling_mean`, etc.).
    - **Transformations appliquées** : Imputation médiane, extraction temporelle (`is_peak_hour`, `is_weekend`), retards et moyennes glissantes.
    - **Sortie** : Valeur prédite en kW avec horodatage UTC, latence d'inférence en ms et identifiant de traçabilité UUID.
    """,
    responses={
        200: {
            "description": "Prédiction calculée avec succès",
            "model": PredictionResponseSchema,
        }
    },
)
def predict_forecasting(
    payload: ForecastingRequest,
    model_manager: ModelManager = Depends(get_model_manager),
) -> PredictionResponseSchema:
    raw_data = payload.model_dump(exclude_unset=True)
    history = raw_data.pop("history", None)
    strict_bounds = raw_data.pop("strict_bounds", False)

    result = model_manager.predict(
        input_data=raw_data,
        history=history,
        strict_bounds=strict_bounds,
    )

    metadata_schema = PredictionMetadataSchema(
        request_id=result.metadata.request_id,
        execution_time_ms=result.metadata.execution_time_ms,
        timestamp=result.metadata.timestamp,
        feature_count=result.metadata.feature_count,
        data_hash=result.metadata.data_hash,
    )

    return PredictionResponseSchema(
        request_id=result.request_id,
        prediction=result.predicted_value,
        unit=result.unit,
        model_name=result.model_name,
        model_version=result.model_version,
        metadata=metadata_schema,
    )


# =====================================================================
# 2. Endpoint : Détection d'Anomalies (Isolation Forest)
# =====================================================================

@router.post(
    "/detect-anomaly",
    response_model=AnomalyResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Détection d'anomalies de consommation et de comportement sensoriel",
    description="""
    Exécute le modèle **Isolation Forest (v2.0.0)** pour identifier les dérives comportementales.
    
    - **Analyse multi-paramétrique** : Puissance (`power_kw`), Température (`temperature_c`), Vibrations (`vibration_hz`), Pression (`pressure_bar`), et variations de charge.
    - **Sortie** : Indicateur booléen `is_anomaly`, score brut de décision, probabilité calibrée, indice de confiance et niveau de sévérité métier (`normal`, `faible`, `modérée`, `critique`).
    """,
    responses={
        200: {
            "description": "Diagnostic d'anomalie produit avec succès",
            "model": AnomalyResponseSchema,
        }
    },
)
def detect_anomaly(
    payload: AnomalyDetectionRequest,
    model_manager: ModelManager = Depends(get_model_manager),
) -> AnomalyResponseSchema:
    raw_data = payload.model_dump(exclude_unset=True)
    previous_power = raw_data.pop("previous_power", None)
    strict_bounds = raw_data.pop("strict_bounds", False)

    result = model_manager.detect_anomaly(
        input_data=raw_data,
        previous_power=previous_power,
        strict_bounds=strict_bounds,
    )

    metadata_schema = PredictionMetadataSchema(
        request_id=result.metadata.request_id,
        execution_time_ms=result.metadata.execution_time_ms,
        timestamp=result.metadata.timestamp,
        feature_count=result.metadata.feature_count,
        data_hash=result.metadata.data_hash,
    )

    return AnomalyResponseSchema(
        request_id=result.request_id,
        is_anomaly=result.is_anomaly,
        anomaly_score=result.score,
        anomaly_probability=result.probability,
        confidence=result.confidence,
        severity=result.severity,
        model_name=result.model_name,
        model_version=result.model_version,
        metadata=metadata_schema,
    )


# =====================================================================
# 3. Endpoint : Bilan de Santé Opérationnel (Health)
# =====================================================================

@router.get(
    "/health",
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
    summary="Diagnostic de santé et disponibilité de la couche ML",
    description="""
    Inspecte l'état complet du sous-système Machine Learning :
    - Disponibilité des modèles en mémoire (`models`)
    - Accessibilité du registre de métadonnées (`registry`)
    - Validité des schémas de caractéristiques (`feature_schema`)
    - Intégrité des fichiers d'artefacts physiques (`artifacts`)
    - Taux d'erreurs et métriques opérationnelles (`metrics`)
    """,
    responses={
        200: {"description": "Système opérationnel ou dégradé"},
        503: {"description": "Système indisponible"},
    },
)
def get_ml_health(
    response: Response,
    model_manager: ModelManager = Depends(get_model_manager),
) -> HealthStatus:
    health = model_manager.health_check()
    if health.status == "unhealthy":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif health.status == "degraded":
        response.status_code = status.HTTP_200_OK
    return health


# =====================================================================
# 4. Endpoints : Registre des Modèles (Models)
# =====================================================================

@router.get(
    "/models",
    response_model=List[ModelInfo],
    status_code=status.HTTP_200_OK,
    summary="Liste des modèles répertoriés dans le registre ML",
    description="Retourne l'ensemble des modèles actifs, leurs versions, statuts de qualification et caractéristiques requises.",
)
def list_models(
    model_manager: ModelManager = Depends(get_model_manager),
) -> List[ModelInfo]:
    return model_manager.list_models()


@router.get(
    "/models/{model_name}",
    response_model=ModelInfo,
    status_code=status.HTTP_200_OK,
    summary="Métadonnées et métriques détaillées d'un modèle",
    description="Retourne les informations de model card, métriques d'évaluation et liste des variables pour un modèle donné.",
    responses={
        404: {"model": StandardErrorResponse, "description": "Modèle introuvable"},
    },
)
def get_model_details(
    model_name: str,
    model_manager: ModelManager = Depends(get_model_manager),
) -> ModelInfo:
    try:
        return model_manager.get_model_info(model_name)
    except Exception as e:
        logger.warning(f"[API] Modèle non trouvé : {model_name} ({e})")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Le modèle '{model_name}' est introuvable dans le registre.",
        ) from e


# =====================================================================
# 5. Endpoint : Tableau de Bord des Métriques (Metrics)
# =====================================================================

@router.get(
    "/metrics",
    status_code=status.HTTP_200_OK,
    summary="Tableau de bord unifié des métriques IA et observabilité",
    description="""
    Fournit un rapport consolidé en temps réel combinant :
    - **Métriques d'inférence** : Débit, compteurs, latences (p50, p95, p99), taux d'erreur.
    - **Métriques d'évaluation** : Performances d'entraînement (RMSE, MAE, R², F1).
    - **Synthèse d'audit** : Transactions récentes et répartition par modèle.
    - **Diagnostic de santé** : Statut opérationnel global.
    """,
)
def get_ml_metrics(
    model_manager: ModelManager = Depends(get_model_manager),
) -> Dict[str, Any]:
    return model_manager.get_metrics()


# =====================================================================
# 6. Endpoint Sécurisé : Rechargement à Chaud des Modèles (Reload)
# =====================================================================

@router.post(
    "/reload",
    response_model=ReloadResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Rechargement à chaud sécurisé des modèles et schémas",
    description="""
    Recharge l'intégralité des modèles joblib, des schémas et du registre sans redémarrer le service.
    
    **Sécurité** : Endpoint protégé réservé aux administrateurs.
    Nécessite l'en-tête `X-API-Key: <clé>` ou `Authorization: Bearer <token>`.
    """,
    responses={
        401: {"model": StandardErrorResponse, "description": "Authentification requise"},
        403: {"model": StandardErrorResponse, "description": "Accès non autorisé"},
    },
)
def reload_ml_models(
    authenticated: bool = Depends(verify_ml_admin_key),
    model_manager: ModelManager = Depends(get_model_manager),
) -> ReloadResponseSchema:
    logger.info("[API] Déclenchement du rechargement des modèles ML via API...")
    model_manager.reload_models()

    active_models = [m.name for m in model_manager.list_models()]
    version = model_manager.registry.get_latest_version()

    return ReloadResponseSchema(
        status="reloaded",
        message="Tous les modèles, métadonnées et schémas ont été rechargés avec succès en mémoire.",
        timestamp=datetime.now(timezone.utc),
        version=version,
        active_models=active_models,
    )


# =====================================================================
# 7. Endpoint : Journal d'Audit des Inférences (Audit)
# =====================================================================

@router.get(
    "/audit",
    status_code=status.HTTP_200_OK,
    summary="Journal d'audit et traçabilité des transactions d'inférence",
    description="Permet de consulter et filtrer les enregistrements d'audit récents (latence, modèle, statut, empreinte).",
)
def get_audit_logs(
    limit: int = Query(default=50, ge=1, le=500, description="Nombre maximal d'enregistrements"),
    model_name: Optional[str] = Query(default=None, description="Filtre sur le nom du modèle"),
    status_filter: Optional[str] = Query(default=None, alias="status", description="Filtre statut (SUCCESS, ERROR)"),
    operation: Optional[str] = Query(default=None, description="Filtre opération (forecasting, anomaly_detection)"),
    request_id: Optional[str] = Query(default=None, description="Recherche par UUID de requête"),
    model_manager: ModelManager = Depends(get_model_manager),
) -> List[Dict[str, Any]]:
    records = model_manager.audit_logger.get_records(
        limit=limit,
        model_name=model_name,
        status=status_filter,
        operation=operation,
        request_id=request_id,
    )
    return [r.model_dump(mode="json") for r in records]
